from librec_auto.core import ConfigCmd

import numpy as np
from pathlib import Path


class Evaluator:
    """
    Evaluator evaluates a single CV and for a single experiment across a list of metrics.


    The structure for python-side evaluation is as follows:

    * Initialize the EvalCmd
      - For each CV:
        * Initialize an Evaluator <- gets all the data here
          - Runs Metric1 (i.e., implementation of ListBasedMetric)
          - Runs Metric2 (i.e., implementation of RowBasedMetric)
          - ...

    AS 3-26-21
    """
    def __init__(self, config: ConfigCmd, metrics: list, cv_directory: Path,
                 experiment_num: int, cv_num: int) -> None:
        """Init

        Args:
            config (ConfigCmd): The configuration for the study.
            metrics (list): A list of dicts with metric information. See eval_cmd.get_metrics for detailed schema.
            cv_directory (Path): The path to the directory containing the CV split files.
            experiment_num (int): The experiment number of this experiment, zero indexed.
            cv_num (int): The CV number for this CV, one indexed.
        """
        self._config = config
        self._metrics = metrics
        self._cv_directory = cv_directory
        self._experiment_num = experiment_num
        self._cv_num = cv_num

        self._test_data = np.genfromtxt(self._cv_directory / 'test.txt',
                                        delimiter='\t')

    def evaluate(self):
        """
        Perform the actual evaluation.

        todo: parallelize this
        """
        for metric_dict in self._metrics:
            # Create a new instance of this metric
            metric = metric_dict['class'](metric_dict['params'],
                                          self.get_test_data(),
                                          self.get_result_data())
            result = metric.evaluate()
            print(metric_dict['class'], result)
            # todo identify a way to save/output the metric results

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
        return np.genfromtxt(
            self._config.get_files().get_study_path() /
            self._config.get_files().get_exp_paths(
                self._experiment_num).get_path('librec_result') /
            'out-{0}.txt'.format(self._cv_num),
            delimiter=",")
