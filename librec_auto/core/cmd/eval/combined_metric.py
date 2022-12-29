import argparse
import numpy as np
import math
from collections import Counter

from librec_auto.core.eval import ListBasedMetric
from librec_auto.core import read_config_file, ConfigCmd
from ndcg_metric import NdcgMetric

class combined_metric():
    def __init__(self, params: dict, conf: ConfigCmd, test_data: np.array,
                 result_data: np.array, output_file, max_old) -> None:
        self._name = "combined_metric"
        self.accuracy_metric = NdcgMetric(params, conf, test_data, result_data, output_file)
        self.max_old = max_old
        self.conf = conf
        # self.fairness_metric = pass
        #where the heck is statistical parity
        
    def evaluate(self):
        return min(0,(self.accuracy_metric.evaluate_user() - 0.9*self.max_old)) + self.fairness_metric.evaluate_user()

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
    parser.add_argument('--list_size', help='Size of the list for NDCG.')

    input_args = parser.parse_args()
    print(vars(input_args))
    return vars(input_args)

if __name__ == '__main__':
    args = read_args()
    # parse_protected
    # protected_feature_file can be parsed here
    config = read_config_file(args['conf'], '.')
    
    params = {'list_size': args['list_size']}

    test_data = ListBasedMetric.read_data_from_file(
        args['test']
    )

    # original_data = args['results']

    # original_data.replace('result', 'out')

    # original_data = ListBasedMetric.read_data_from_file(
    #     original_data,
    #     delimiter=','
    # )

    result_data = ListBasedMetric.read_data_from_file(
        args['result'],
        delimiter=','
    )

    print("Creating metric")
    custom = combined_metric(params, config, test_data, result_data,
                        args['output_file'])

    print("applying metric")
    custom.evaluate()