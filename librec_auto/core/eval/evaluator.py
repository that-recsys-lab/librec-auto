from librec_auto.core import ConfigCmd
from .metrics.list_based_metric import ListBasedMetric
from librec_auto.core.util import ScriptFailureException, safe_run_subprocess
import re
import numpy as np
from pathlib import Path
import sys
import subprocess


class Evaluator:
    """
    Evaluator evaluates a single CV and for a single experiment across a list of metrics.


    The structure for python-side evaluation is as follows:

    * Initialize the EvalCmd
      - For each CV:
        * Initialize an Evaluator <- gets all the data here
          - Runs Metric1 (i.e., implementation of ListBasedMetric)
          - Runs Metric2
          - ...
    Must all be of the same type (ListBased or RowBased)

    AS 3-26-21
    """
    def __init__(self, conf: ConfigCmd, metrics: list, cv_directory: Path,
                 experiment_num: int, cv_num: int) -> None:
        """Init

        Args:
            config (ConfigCmd): The configuration for the study.
            metrics (list): A list of dicts with metric information. See eval_cmd.get_metrics for detailed schema.
            cv_directory (Path): The path to the directory containing the CV split files.
            experiment_num (int): The experiment number of this experiment, zero indexed.
            cv_num (int): The CV number for this CV, one indexed.
        """
        self._conf = conf
        self._metrics = metrics
        self._cv_directory = cv_directory
        self._experiment_num = experiment_num
        self._cv_num = cv_num

        files = self._conf.get_files()

        self._result_data_file = files.get_study_path() / \
            files.get_exp_paths(self._experiment_num).get_path('librec_result') / \
                                 'out-{0}.txt'.format(self._cv_num)

        # This is the destination for custom script output.
        # The custom class files will save results here (as a pickle)
        # so that the evaluator can retreive them.
        self._temp_output_file = files.get_study_path() / \
            files.get_exp_paths(self._experiment_num).get_path('librec_result') / \
                                 'py-eval-temp.pickle'
        self._test_data_file = self._cv_directory / 'test.txt'
        self._test_data = np.genfromtxt(self._test_data_file, delimiter='\t')

    def evaluate(self):
        """
        Perform the actual evaluation.

        todo: parallelize this
        """

        metric_results = []

        for metric_dict in self._metrics:
            if metric_dict.get('script') != None:
                # Run this script with the params
                exec_path = self._conf.get_files().get_study_path()

                proc_spec = [sys.executable, metric_dict['script']]
                params = [
                    '--conf', self._conf.get_files().get_config_file_path().name,
                    '--test', str(self._test_data_file),
                    '--result', str(self._result_data_file.absolute()),
                    '--output-file', str(self._temp_output_file.absolute())
                ]

                for key in metric_dict['params']:
                    params.append('--' + key)
                    params.append(metric_dict['params'][key])

                script_run = safe_run_subprocess(proc_spec + params, 
                                                 str(exec_path.absolute()))
                
                script_path = metric_dict['script']
                script_name = metric_dict['script'].name
                if script_run != 0:
                    raise ScriptFailureException(script_name, f"Script at {script_path} failed with errors", script_run)


                custom_result = ListBasedMetric.read_custom_results(
                    self._temp_output_file.absolute())
                script_name = metric_dict['script'].name
                metric_results.append({
                    'name': script_name,
                    'value': custom_result
                })
                print(script_name, ':', custom_result)

            else:
                # Create a new instance of this metric
                metric = metric_dict['class'](metric_dict['params'],
                                              self.get_test_data(),
                                              self.get_result_data())
                result = metric.evaluate()

                metric_name = str(metric_dict['class'])

                # Try to coerce the class name into a string
                try:
                    metric_name = re.search(r"<class '.*\.([A-z]*)'>",
                                            metric_name).group(1)
                except Exception:
                    pass

                metric_results.append({'name': metric_name, 'value': result})

                print(metric_name, result)

        return metric_results

    def get_test_data(self) -> np.array:
        """
        Loads test data from the cv_n directories
        Returns a numpy array (shape 3 x n: user_id, item_id, score)
        """
        return self._test_data

    def get_result_data(self) -> np.array:
        """
        Loads result data from the main/expnnnnn/result directories
        This should be a numpy array (shape 3 x n: user_id, item_id, score)
        """
        return np.genfromtxt(self._result_data_file, delimiter=",")
