import argparse
from typing import Tuple
import numpy as np

from librec_auto.core.eval import ListBasedMetric
from librec_auto.core import read_config_file, ConfigCmd


class ExpectedExposureMetric(ListBasedMetric):
    """Expected Exposure Loss Metric

    From Diaz, Fernando, et al. "Evaluating stochastic rankings with expected exposure." Proceedings of the 29th ACM International Conference on Information & Knowledge Management. 2020.

    https://arxiv.org/pdf/2004.13157.pdf

    See Equation (1).

    AS 10-26-21
    """
    def __init__(self, params: dict, conf: ConfigCmd, test_data: np.array,
                 result_data: np.array, output_file) -> None:
        super().__init__(params, conf, test_data, result_data, output_file)
        self._name = 'Expected Exposure'

    def evaluate(self):
        # get max ranking
        max_result = np.max(test_data[:, 2])

        # get min ranking
        min_result = np.min(test_data[:, 2])

        def normalize_results(data):
            return [(i - min_result) / (max_result - min_result) for i in data]

        def get_epsilon(uir_array, items=None):
            if items is None:
                items = np.unique(uir_array[:, 1])

            epsilon = []
            for item in items:
                relevant_indices = np.where(uir_array[:, 1] == item)[0]
                item_rankings = [uir_array[i][2] for i in relevant_indices]

                exposure_values = normalize_results(item_rankings)

                if len(exposure_values) > 0:
                    average_exposure = np.average(exposure_values)
                else:
                    average_exposure = 0
                epsilon.append(average_exposure)

            return np.array(epsilon), items

        result_epsilon, result_items = get_epsilon(result_data)

        # Use the same items for both epsilon vectors
        test_epsilon, _ = get_epsilon(test_data, items=result_items)

        squared_error = (result_epsilon - test_epsilon)**2
        mse = squared_error.mean()

        self._save_custom_results(mse)
        return mse


def read_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='My custom metric')
    parser.add_argument('--conf', help='Path to config file')
    parser.add_argument('--test', help='Path to test.')
    parser.add_argument('--result', help='Path to results.')
    parser.add_argument('--output-file', help='The output pickle file.')

    input_args = parser.parse_args()
    print(vars(input_args))
    return vars(input_args)


if __name__ == '__main__':
    args = read_args()
    # parse_protected
    # protected_feature_file can be parsed here
    config = read_config_file(args['conf'], '.')

    test_data = ListBasedMetric.read_data_from_file(args['test'])
    result_data = ListBasedMetric.read_data_from_file(args['result'],
                                                      delimiter=',')

    print("Creating metric")

    custom = ExpectedExposureMetric({}, config, test_data, result_data,
                                    args['output_file'])

    print("applying metric")
    custom.evaluate()
