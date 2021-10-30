import argparse
import numpy as np
import math
from collections import Counter

from librec_auto.core.eval import ListBasedMetric
from librec_auto.core import read_config_file, ConfigCmd

class alpha_IA(ListBasedMetric):

    def __init__(self, params: dict, conf: ConfigCmd, test_data: np.array,
                 result_data: np.array, output_file) -> None:
        super().__init__(params, conf, test_data, result_data, output_file)
        self._name = 'alpha-IA'
        self.totals = {}

    def pre_row_processing(self):
        self.fraction_items = 0

    def evaluate_user(self, test_user_data: np.array,
                      result_user_data: np.array) -> float:
        user_list_size = int(self._params['list_size'])
        alpha = int(self._params['alpha'])

        counter = Counter(result_user_data[:, 1])

        i = 0

        for key in counter.keys():
            if key in self.totals:
                self.totals[key] += counter[key]

                if self.totals[key] >= alpha:
                    i += 1
            else:
                self.totals[key] = counter[key]

                if self.totals[key] >= alpha:
                    i += 1

        return i

    def postprocessing(self):
        return self._values[-1]/len(self._values)
        
def read_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='My custom metric')
    parser.add_argument('--conf', help='Path to config file')
    parser.add_argument('--test', help='Path to test.')
    parser.add_argument('--result', help='Path to results.')
    parser.add_argument('--output-file', help='The output pickle file.')

    # Custom params defined in the config go here
    parser.add_argument('--alpha', help='Specified alpha value')
    parser.add_argument('--list_size', help='Size of the list for alpha-IA.')

    input_args = parser.parse_args()
    print(vars(input_args))
    return vars(input_args)

if __name__ == '__main__':
    args = read_args()
    # parse_protected
    # protected_feature_file can be parsed here
    config = read_config_file(args['conf'], '.')
    
    params = {'alpha': args['alpha'], 'list_size': args['list_size']}

    test_data = ListBasedMetric.read_data_from_file(
        args['test']
    )
    result_data = ListBasedMetric.read_data_from_file(
        args['result'],
        delimiter=','
    )

    print("Creating metric")

    custom = alpha_IA(params, config, test_data, result_data,
                        args['output_file'])

    print("applying metric")
    custom.evaluate()