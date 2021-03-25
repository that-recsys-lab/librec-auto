import numpy as np


class ListBasedMetric:
    def __init__(self, params: dict, data: np.array) -> None:
        self._params = params
        self._data = data
        self._name = 'Generic Metric'

    def get_params(self) -> dict:
        return self._params

    def evaluate(self):
        # Overridden by instances
        print('Evaluating metric', self._name, '...')
        # use self._data
        pass
