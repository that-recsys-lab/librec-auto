from .metric import Metric


class RmseMetric(Metric):
    def __init__(self, params: dict) -> None:
        super().__init__(params)
        self._name = 'RMSE'

    def evaluate(self):
        # Todo add custom eval here
        return super().evaluate()
