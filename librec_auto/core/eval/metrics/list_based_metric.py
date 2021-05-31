import numpy as np
import pickle
from librec_auto.core import ConfigCmd


class ListBasedMetric:
    def __init__(self, params: dict, conf: ConfigCmd, test_data: np.array,
                 result_data: np.array, output_file) -> None:
        self._params = params
        self._conf = conf
        self._test_data = test_data
        self._result_data = result_data
        self._name = 'Generic Metric'
        self._output_file = output_file
        self._values = []

    @staticmethod
    def read_data_from_file(file_name, delimiter='\t'):
        data = np.genfromtxt(file_name, delimiter=delimiter)
        return data

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

    def _save_custom_results(self, result: float):
        with open(self._output_file, 'wb') as file:
            pickle.dump(result, file)

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

        result = self.postprocessing()
        self._save_custom_results(result)
        return result

    @staticmethod
    def read_custom_results(output_file: str):
        with open(output_file, 'rb') as file:
            return pickle.load(file)
