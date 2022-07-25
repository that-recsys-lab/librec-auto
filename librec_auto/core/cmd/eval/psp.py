from librec_auto.core.cmd.rerank import Rerank_Helper, User_Helper, Reranker

import numpy as np
import pandas as pd
from scipy.spatial import distance
from sklearn.preprocessing import MinMaxScaler
import argparse
from librec_auto.core import read_config_file
import os
import re
from pathlib import Path
from librec_auto.core.util.xml_utils import single_xpath
from librec_auto.core.eval import ListBasedMetric
from librec_auto.core import read_config_file, ConfigCmd
import warnings

warnings.filterwarnings('ignore')
import multiprocessing
class PSPMetric(ListBasedMetric):
    def __init__(self, params: dict, conf: ConfigCmd, test_data: np.array,
                 result_data: np.array, output_file, item_feature_df,itemids, protected) -> None:
        # print(params)
        super().__init__(params, conf, test_data, result_data, output_file)
        self._name = 'PSP'
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

    def evaluate_user(self, test_user_data: np.array,
                      result_user_data: np.array) -> float:
        rec_num = int(self._params['list_size'])

        # modified from https://github.com/nasimsonboli/OFAiR/blob/main/source%20code/OFAiR_Evaluation.ipynb
        protected_num = 0
        unprotected_num = 0
        print(result_user_data)
        total = min(rec_num, len(result_user_data))
        for j in range(total):
            if int(result_user_data[j][1]) in self.protected_set:
                protected_num += 1
            else:
                unprotected_num += 1

        protected_ratio = protected_num / total
        unprotected_ratio = unprotected_num / total
        # print(self.protected_set)
        # print(result_user_data)
        t = []
        for j in range(total):
            if int(result_user_data[j][1]) in self.protected_set:
                t.append(True)
            else:
                t.append(False)
        print(t)
            
        print(protected_num, unprotected_num)
        print(protected_ratio,unprotected_ratio,protected_ratio-unprotected_ratio)
        print()
        return protected_ratio - unprotected_ratio


    def postprocessing(self):
        # print(self._values)
        print(sum(self._values)/len(self._values))
        print(np.average(self._values))
        return np.average(self._values)

def read_data_from_file(file_name, delimiter='\t'):
    d = []
    with open(file_name, "r") as f:
        for line in f:
            split_line = line.split(delimiter)
            split_line[1] = int(split_line[1])
            d.append(split_line)

    d = np.array(d)
    return d

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
    parser.add_argument('--list_size', help='Size of the list for NDCG.')

    input_args = parser.parse_args()

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

# def check_percentage(item_feature_df):
#     store_countries = {}
#     total = 0
#     for i in range(len(item_feature_df)):
#         if "COUNTRY" in item_feature_df.iloc[i]['feature']:
#             if item_feature_df.iloc[i]['feature'] not in store_countries:
#                 store_countries[item_feature_df.iloc[i]['feature']] = 0
#             else:
#                 store_countries[item_feature_df.iloc[i]['feature']] += 1

#             total += 1

#     for key in store_countries:
#         store_countries[key] = store_countries[key]/total

#     store_underrepresented = []

#     for key in store_countries:
#         if store_countries[key] <= 0.01:
#             store_underrepresented.append(key)

#     return store_underrepresented

def main():
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
    result_data = read_data_from_file(
        args['result'],
        delimiter=','
    )

    item_feature_df, itemids = load_item_features(config, data_path)
    if item_feature_df is None:
        exit(-1)

    # protected = check_percentage(item_feature_df)
    print("Creating metric")

    custom = PSPMetric(params, config, test_data, result_data,
                        args['output_file'], item_feature_df, itemids, protected)

    print("applying metric")
    custom.evaluate()


if __name__ == '__main__':
    main()


