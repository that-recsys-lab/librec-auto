from librec_auto.core import ConfigCmd

from numpy import genfromtxt
from pathlib import Path


class Evaluator:
    # Todo somehow load the data here? (From config?)
    # Todo make the list_based param at the metric level
    def __init__(self, config: ConfigCmd, metrics: list, cv_directory: Path,
                 experiment_num: int, cv_num: int) -> None:
        self._config = config
        self._metrics = metrics
        self._cv_directory = cv_directory
        self._experiment_num = experiment_num
        self._cv_num = cv_num

        self._user_features = genfromtxt(self._cv_directory / 'test.txt',
                                         delimiter=',')

    def evaluate(self):
        # Perform the actual evaluation.
        for metric_dict in self._metrics:
            # Create a new instance of this metric
            metric = metric_dict['class'](metric_dict['params'],
                                          self.get_test_data(),
                                          self.get_result_data())
            metric.evaluate()

    def get_test_data(self):
        """
        This should be a numpy array (shape 3 x n: user_id, item_id, score)
        Load data from the data/split/cv_n directories
        """
        return self._user_features

    def get_result_data(self):
        """
        This should be a numpy array (shape 3 x n: user_id, item_id, score)
        Load data from the main/expnnnnn/result directories
        """
        return genfromtxt(self._config.get_files().get_study_path() /
                          self._config.get_files().get_exp_paths(
                              self._experiment_num).get_path('librec_result') /
                          'out-{0}.txt'.format(self._cv_num),
                          delimiter=",")

    def get_item_features(self):
        self.item_features = "tktktk"
        pass

    # log the individual assessment scores somehow


"""
EvalCmd
    For each CV:
        Evaluator <- gets all the data here
            Metric1 (implementation of ListBasedMetric)  <- receives data as lists (how?)
            Metric2 (implementation of RowBasedMetric)   <- receives data as a list, processes as rows (where does this come from?)
"""
