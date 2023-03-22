import argparse
import numpy as np
import math
import rbo
import pandas as pd

from pathlib import Path
from librec_auto.core.util.xml_utils import single_xpath
from librec_auto.core.eval import ListBasedMetric
from librec_auto.core import read_config_file, ConfigCmd
import warnings
class LowestItemPromoted(ListBasedMetric):
    def __init__(self, params: dict, conf: ConfigCmd, original_data: np.array,
                 reranked_data: np.array, output_file, item_feature_df, itemids, protected) -> None:
            # print(params)
        super().__init__(params, conf, test_data, reranked_data, output_file)
        self._name = 'LowestItemPromoted'
        self._item_feature_df = item_feature_df
            # print(self._item_feature_df)
        self._protected = protected

        self.protected_set = set()

        item_id_list = itemids

        self.item_feature_list = item_feature_df["feature"].values.tolist()

        if isinstance(protected, str):
            for i in range(len(self._item_feature_df)):
                if self.item_feature_list[i] == protected:
                    self.protected_set.add(int(item_id_list[i]))
        else:
            for i in range(len(self._item_feature_df)):
                if self.item_feature_list in protected:
                    self.protected_set.add(int(item_id_list[i]))

        # modified from https://github.com/nasimsonboli/OFAiR/blob/main/source%20code/OFAiR_Evaluation.ipynb

    def evaluate_user(self, original_user_data: np.array,
                      reranked_user_data: np.array) -> float:

        original = original_user_data[:, 1]

        reranked = reranked_user_data[:, 1]

        # modified from https://github.com/nasimsonboli/OFAiR/blob/main/source%20code/OFAiR_Evaluation.ipynb

        for element in reversed(original):
            if element in reranked:
                if int(original[element][1]) in self.protected_set:
                    result = original.index(element)

        if self._user_file is not None:
            file.write(result)
        return result

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
    parser.add_argument('--protected_feature', help='protected feature')

    # Custom params defined in the config go here
    parser.add_argument('--list_size', help='Size of the list for lowest item.')
    # parser.add_argument('--user_output')

    input_args = parser.parse_args()
    print(vars(input_args))
    return vars(input_args)

def load_item_features(config, data_path):
    item_feature_file = single_xpath(
        config.get_xml(), '/librec-auto/features/item-feature-file').text
    item_feature_path = data_path / item_feature_file

    if not item_feature_path.exists():
        print("Cannot locate item features. Path: " + item_feature_path)
        return None

    item_feature_df = pd.read_csv(item_feature_path,
                                  names=['itemid', 'feature', 'value'])

    item_ids = item_feature_df['itemid'].tolist()
    item_feature_df.set_index('itemid', inplace=True)
    return item_feature_df, item_ids


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

    config = read_config_file(args['conf'], '.')

    params = {'list_size': args['list_size']}

    protected = args['protected_feature']

    data_dir = single_xpath(config.get_xml(), '/librec-auto/data/data-dir').text

    data_path = Path(data_dir)
    data_path = data_path.resolve()

    test_data = read_data_from_file(
        args['test']
    )


    item_feature_df, itemids = load_item_features(config, data_path)
    if item_feature_df is None:
            exit(-1)

    reranked_data = read_data_from_file(
        args['result'],
        delimiter = ','
    )

    original_data = args['result']
    original_data = original_data.replace('result', 'original')
    original_data = ListBasedMetric.read_data_from_file(
        original_data,
        delimiter=','
    )

    print("Creating metric")

    if "user_output" in args:
        with open(user_output_file, 'w') as file:
            custom = LowestItemPromoted(params, config, reranked_data, original_data,
                            args['output_file'], file, item_feature_df, itemids, protected)
            custom.evaluate()
    else:

        custom = LowestItemPromoted(params, config, reranked_data, original_data,
                            args['output_file'], item_feature_df, itemids, protected)
        custom.evaluate()

    print("applying metric")
