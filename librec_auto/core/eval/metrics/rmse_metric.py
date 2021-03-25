import numpy as np
from .row_based_metric import RowBasedMetric


class RmseMetric(RowBasedMetric):
    def __init__(self, params: dict, test_data: np.array,
                 result_data: np.array) -> None:
        super().__init__(params, test_data, result_data)
        self._name = 'RMSE'

    def evaluate_row(self, test: np.array, result: np.array):
        test_ranking = test[2]
        result_ranking = result[2]
        return (test_ranking - result_ranking)**2

    def post_row_processing(self, values):
        T = len(values)
        return (sum(values) / T)**0.5
