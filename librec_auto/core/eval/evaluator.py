from librec_auto.core import ConfigCmd


class Evaluator:
    # Todo somehow load the data here? (From config?)
    def __init__(self,
                 config: ConfigCmd,
                 metrics: list,
                 list_based=True) -> None:
        self.metrics = metrics  #  A list of metric class instances
        self.list_based = list_based

    def evaluate(self):
        # performing actual evaluation here...
        for metric in self._metrics:
            metric.evaluate()

    def get_user_features(self):
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
