import numpy as np
from .row_based_metric import RowBasedMetric


class RmseMetric(RowBasedMetric):
    def __init__(self, params: dict, test_data: np.array,
                 result_data: np.array) -> None:
        super().__init__(params, test_data, result_data)
        self._name = 'RMSE'

    def evaluate_row(self):
        # Todo add custom eval here
        return 3
