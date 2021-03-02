from librec_auto.core import ConfigCmd
from pathlib import Path


class Evaluator:
    # Todo somehow load the data here? (From config?)
    # Todo make the list_based param at the metric level
    def __init__(self, config: ConfigCmd, metrics: list,
                 cv_directory: Path) -> None:
        self._config = config
        self._metrics = metrics
        self._cv_directory = cv_directory

    def evaluate(self):
        # performing actual evaluation here...
        for metric_dict in self._metrics:
            # Create a new instance of this metric
            metric = metric_dict['class'](metric_dict['params'])
            metric.evaluate()

    def get_user_features(self):
        # todo load data from self._cv_directory
        self.user_features = "tktktk"
        """
        This should be a list with length = the number of CVs
            Each item should be a dataframe or numpy array (shape 3 x n: user_id, item_id, score)
        Load data from the data/split/cv_n directories
        """
        pass

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
