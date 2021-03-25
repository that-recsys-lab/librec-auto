import numpy as np


class ListBasedMetric:
    def __init__(self, params: dict, test_data: np.array,
                 result_data: np.array) -> None:
        self._params = params
        self._test_data = test_data
        self._result_data = result_data
        self._name = 'Generic Metric'

    def get_params(self) -> dict:
        return self._params

    def evaluate(self):
        # Overridden by instances
        print('Evaluating metric', self._name, '...')
        # use self._data
        pass
