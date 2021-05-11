import numpy as np


class RowBasedMetric():
    """
    Generic class for python-side evaluation with row-based metrics.
    """
    def __init__(self, params: dict, test_data: np.array,
                 result_data: np.array) -> None:
        self._params = params
        self._test_data = test_data
        self._result_data = result_data
        self._result = None
        self._scores = []  # This holds the metric scores for each row

    def pre_row_processing(self):
        """
        Perform any metric setup here.

        i.e. setting the initial value for a running total.
        """
        pass

    def evaluate_row(self, test_row: np.array, result_row: np.array):
        """Perform any row-based calculations here.

        Args:
            test_row (np.array): The test row data.
            result_row (np.array): The result row data.
        """
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

        rows_count = len(self._result_data)

        for i in range(rows_count):
            self._scores.append(
                self.evaluate_row(self._result_data[i], self._test_data[i]))

        return self.post_row_processing(self._scores)
