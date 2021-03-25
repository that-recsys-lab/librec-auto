import numpy as np

from .list_based_metric import ListBasedMetric


class NdcgMetric(ListBasedMetric):
    def __init__(self, params: dict, test_data: np.array,
                 result_data: np.array) -> None:
        super().__init__(params, test_data, result_data)
        self._name = 'NDCG'

    def evaluate(self):
        # Todo add custom eval here
        return super().evaluate()
