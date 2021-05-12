import numpy as np


class ListBasedMetric:
    def __init__(self, params: dict, test_data: np.array,
                 result_data: np.array) -> None:
        self._params = params
        self._test_data = test_data
        self._result_data = result_data
        self._name = 'Generic Metric'
        self._values = []

    def get_params(self) -> dict:
        return self._params

    def evaluate_user(self, test_user_data: np.array,
                      result_user_data: np.array) -> float:
        """Overridden by instance"""

    def preprocessing(self):
        """
        Perform any metric setup here.
        """
        pass

    def postprocessing(self):
        """
        Perform any metric teardown here.
        """
        pass

    def evaluate(self):
        print('Evaluating metric', self._name, '...')

        self.preprocessing()

        # A unique list of users in the data
        users = np.unique(self._test_data[:, 0])

        for user in users:
            # get all of the rows where user_id = user for test and result data
            test_mask = self._test_data[:, 0] == user
            test_user_data = self._test_data[test_mask, :]

            result_mask = self._result_data[:, 0] == user
            result_user_data = self._result_data[result_mask, :]

            self._values.append(
                self.evaluate_user(test_user_data, result_user_data))

        return self.postprocessing()
