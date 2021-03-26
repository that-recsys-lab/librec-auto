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

        for row in self._test_data:
            # Find the result row with the same user and item IDs
            user_id = row[0]
            item_id = row[1]

            # todo optimize this
            match = self._result_data[(self._result_data[:, 0] == user_id)
                                      & (self._result_data[:, 1] == item_id)]

            # If there's a match...
            if len(match) != 0:
                # Pass the test_row and the result_row to evaluate_row
                self._scores.append(self.evaluate_row(match[0], row))

        return self.post_row_processing(self._scores)
