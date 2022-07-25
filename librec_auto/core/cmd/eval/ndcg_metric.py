import argparse
import numpy as np
import math

from librec_auto.core.eval import ListBasedMetric
from librec_auto.core import read_config_file, ConfigCmd

class NdcgMetric(ListBasedMetric):
    def __init__(self, params: dict, conf: ConfigCmd, test_data: np.array,
                 result_data: np.array, output_file) -> None:
        # print(params)
        super().__init__(params, conf, test_data, result_data, output_file)
        self._name = 'NDCG'

    def evaluate_user(self, test_user_data: np.array,
                      result_user_data: np.array) -> float:
        rec_num = int(self._params['list_size'])

        # modified from https://github.com/nasimsonboli/OFAiR/blob/main/source%20code/OFAiR_Evaluation.ipynb
        idealOrder = test_user_data
        idealDCG = 0.0

        
        for j in range(min(rec_num, len(test_user_data))):
            idealDCG += ((math.pow(2.0, 1) - 1) /
                         math.log(2.0 + j))

        recDCG = 0.0
        test_user_items = set(list(test_user_data[:, 1]))


        t = []
        for j in range(rec_num):
            item = result_user_data[j][1]
            t.append(item)

            if item in test_user_items:
                recDCG += ((math.pow(2.0, 1) - 1) / math.log(1.0 + j + 1))

        return (recDCG / idealDCG)

    def postprocessing(self):
        print(np.average(self._values))
        return np.average(self._values)

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

def read_data_from_file(file_name, delimiter='\t'):
    d = []
    print(file_name)
    with open(file_name, "r") as f:
        for line in f:
            split_line = line.split(delimiter)
            split_line[1] = int(split_line[1])
            d.append(split_line)
            
    d = np.array(d)
    return d

if __name__ == '__main__':
    args = read_args()
    # print(args)
    # parse_protected
    # protected_feature_file can be parsed here

    config = read_config_file(args['conf'], '.')
    
    params = {'list_size': args['list_size']}

    test_data = read_data_from_file(
        args['test']
    )
    result_data = read_data_from_file(
        args['result'],
        delimiter=','
    )

    print("Creating metric")

    custom = NdcgMetric(params, config, test_data, result_data,
                        args['output_file'])

    print("applying metric")
    custom.evaluate()