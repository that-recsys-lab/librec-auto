from pathlib import Path
import os
import json

#from librec_auto.core.eval.metrics.rmse_metric import RmseMetric
from librec_auto.core import ConfigCmd
from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Status, utils

#from librec_auto.core.eval.metrics.ndcg_metric import NdcgMetric
#from librec_auto.core.eval.metrics.rmse_metric import RmseMetric
from librec_auto.core.eval.evaluator import Evaluator

# todo add all metrics here
# Not sure we want to support this
#metric_name_to_class = {'ndcg': NdcgMetric, 'rmse': RmseMetric}


class EvalCmd(Cmd):
    def __init__(self, args, config):
        self._config = config
        self._args = args  # Evaluation arguments

    def __str__(self):
        return f'EvalCmd()'

    def setup(self, args):
        pass

    def dry_run(self, config):
        print(f'librec-auto (DR): Running python eval command {self}')

    def get_metrics(self) -> list:
        """
        Gets a list of the metrics to be evaluated.

        Structure like:
        
        ```
        [
            {
                element: <XML element for the metric>,
                class: <python class for the metric,
                params: <dict with parameters>
            },
            ...
        ]
        ```
        """
        def get_params(metric_element) -> dict:
            """
            Returns a params dict from the metric_element's params child.
            """
            params_elements = metric_element.xpath('param')
            if params_elements is None:
                return {}
            params = {}
            for child in params_elements:
                params[child.get('name')] = child.text
                print("param name: " + child.text)
            return params

        metric_elements = self._config.get_python_metrics()

        metric_classes = []

        for metric_element in metric_elements:
            script_path = utils.get_script_path(metric_element, 'eval')
            metric_classes.append({
                'script':
                    script_path,
                'params':
                    get_params(metric_element)
            })
                # Not sure we want to support this
            #            if metric_element.find('script-name') != None:
            # This is a custom metric with a passed script
            # else:
            #     metric_name = metric_element.find('name').text
            #     metric_classes.append({
            #         'element':
            #         metric_element,
            #         'class':
            #         metric_name_to_class[metric_name],
            #         'params':
            #         get_params(metric_element)
            #     })

        return metric_classes

    def save_results(self, study_count: int, experiment_results: list) -> None:
        log_file = self._config.get_files().get_exp_paths(
            study_count).get_custom_metrics_log_path()

        with open(log_file, 'w') as file:
            json.dump(experiment_results, file)

    def execute(self, config: ConfigCmd):
        self._config = config
        self.status = Cmd.STATUS_INPROC

        metrics = self.get_metrics()
        # Must use absolute paths because these will be passed to a script
        cv_dirs = config.get_cv_directories(absolute=True)

        # todo run this all in parallel

        num_of_experiments = self._config.get_sub_exp_count()

        # Run the evaluator for every cv in every experiment.
        for experiment_num in range(num_of_experiments):
            # Each item in this list represents a cv in the experiment.
            experiment_results = []

            for cv_dir in cv_dirs:
                cv_num = str(cv_dir)[-1]
                print('For experiment', experiment_num + 1, 'evaluating cv',
                      str(cv_dir)[-1], '...')
                # Create an evaluator for each cv...
                evaluator = Evaluator(config, metrics, cv_dir, experiment_num,
                                      cv_num)
                cv_results = evaluator.evaluate()  # Evaluate it.
                experiment_results.append(cv_results)  # Add to results.

            self.save_results(experiment_num, experiment_results)
            Status.save_status(
                "Python-side metrics completed", experiment_num, config,
                config.get_files().get_exp_paths(experiment_num))

        temp_binary_path = self._config.get_files().get_study_path() / Path(
            'py-eval-temp.pickle')
        if os.path.exists(temp_binary_path):
            # Remove temporary eval binary
            os.remove(temp_binary_path)
