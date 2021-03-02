from librec_auto.core import ConfigCmd
from librec_auto.core.cmd import Cmd

from librec_auto.core.eval.metrics.ndcg_metric import NdcgMetric
from librec_auto.core.eval.metrics.metric import Metric

from typing import List


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

    def get_metric_classes(self) -> List[Metric]:
        metric_elements = self._config.get_python_metrics()

        # todo add all metrics here
        metric_name_to_class = {'ndcg_metric': NdcgMetric}

        metric_classes = []

        for metric_element in metric_elements:
            metric_name = metric_element.find('name').text
            metric_classes.append(metric_name_to_class[metric_name])

        return metric_classes

    def execute(self, config: ConfigCmd):
        self._config = config
        self.status = Cmd.STATUS_INPROC

        metric_classes = self.get_metric_classes()
        cv_dirs = config.get_cv_directories()

        # todo run evaluation for each cv
        # todo run in parallel

        import pdb
        pdb.set_trace()
