from librec_auto.core.eval.metrics.rmse_metric import RmseMetric
from librec_auto.core import ConfigCmd
from librec_auto.core.cmd import Cmd

from librec_auto.core.eval.metrics.ndcg_metric import NdcgMetric
from librec_auto.core.eval.metrics.rmse_metric import RmseMetric
from librec_auto.core.eval.evaluator import Evaluator

# todo add all metrics here
metric_name_to_class = {'ndcg': NdcgMetric, 'rmse': RmseMetric}


class EvalCmd(Cmd):
    def __init__(self, args, config):
        self._config = config
        self._args = args  # Evaluation arguments

    def __str__(self):
        return f'EvalCmd()'

    def setup(self, args):
        pass

    def dry_run(self):
        pass

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
            params_element = metric_element.find('params')
            if params_element is None:
                return {}
            all_children = params_element.findall('*')
            params = {}
            for child in all_children:
                params[child.tag] = child.text
            return params

        metric_elements = self._config.get_python_metrics()

        metric_classes = []

        for metric_element in metric_elements:
            metric_name = metric_element.find('name').text
            metric_classes.append({
                'element': metric_element,
                'class': metric_name_to_class[metric_name],
                'params': get_params(metric_element)
            })

        return metric_classes

    def execute(self, config: ConfigCmd):
        self._config = config
        self.status = Cmd.STATUS_INPROC

        metrics = self.get_metrics()
        cv_dirs = config.get_cv_directories()

        # todo run this all in parallel
        for cv_dir in cv_dirs:
            print('Evaluating cv', str(cv_dir)[-1], '...')
            # Create an evaluator for each cv...
            evaluator = Evaluator(config, metrics, cv_dir)
            evaluator.evaluate()  # Evaluate it.