import numpy as np

from .list_based_metric import ListBasedMetric


class NdcgMetric(ListBasedMetric):
    def __init__(self, params: dict, data: np.array) -> None:
        super().__init__(params, data)
        self._name = 'NDCG'

    def evaluate(self):
        # Todo add custom eval here
        return super().evaluate()
