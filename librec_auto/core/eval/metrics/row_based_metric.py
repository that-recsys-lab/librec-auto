import numpy as np


class RowBasedMetric():
    def __init__(self, params: dict, test_data: np.array,
                 result_data: np.array) -> None:
        self._params = params
        self._data = test_data
        self._result_data = result_data
        self._result = None
        self._scores = []  # This holds the metric scores for each row

    def pre_row_processing(self):
        """
        Perform any metric setup here.

        i.e. setting the initial value for a running total.
        """
        pass

    def evaluate_row(self):
        # To be overridden by the subclass
        pass

    def post_row_processing(self):
        """
        Perform any cumulative calculations here.

        i.e. the square root of the metric so far for RMSE.
        """
        pass

    def evaluate(self):
        self.pre_row_processing()

        print('Evaluating metric', self._name, '...')

        for row in self._data:
            self.evaluate_row()

        self.post_row_processing()
