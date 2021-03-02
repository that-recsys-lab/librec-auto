from .metric import Metric


class NdcgMetric(Metric):
    def __init__(self, params: dict) -> None:
        super().__init__(params)
        self._name = 'NDCG'

    def evaluate(self):
        # Todo add custom eval here
        return super().evaluate()
