import argparse
import numpy as np
import math

from librec_auto.core.eval import ListBasedMetric
from librec_auto.core import read_config_file, ConfigCmd

from librec_auto.core.util.protected_feature import ProtectedFeature

class TestMetric(ListBasedMetric):
    def __init__(self, params: dict, conf: ConfigCmd, test_data: np.array, result_data: np.array, output_file) -> None:
        super().__init__(params, conf, test_data, result_data, output_file)
        self._name = "Test"

    # def 


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
    config = read_config_file(args['conf'], '.')
    temp_directory = config.get_files().get_temp_dir_path()
    protected_feats = ProtectedFeature(ProtectedFeature.parse_protected(config), temp_dir=temp_directory)
    
