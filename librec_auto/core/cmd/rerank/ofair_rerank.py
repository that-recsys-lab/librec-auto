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
import warnings

warnings.filterwarnings('ignore')
import multiprocessing



class OFAIR(Reranker):
    def fun(self):
        def ofair(rec, rerank_helper, user_helper):
            num_remain = len(user_helper.item_list)
            num_curr = len(user_helper.item_so_far)

            if num_curr <= 0:
                scores = rerank_helper.lamb * rec

            else:
                sim = np.zeros([num_remain, num_curr])
                sim_mean = np.zeros(num_remain)

                for i in range(num_remain):
                    for j in range(num_curr):
                        index1 = user_helper.item_list[i]
                        index2 = user_helper.item_so_far[j]
                        sim[i][j] = rerank_helper.update_sim_matrix_dic(index1, index2, rerank_helper.binary)

                    sim_mean[i] = np.mean(sim[i])
                scores = rerank_helper.lamb * rec - (1 - rerank_helper.lamb) * sim_mean

            return scores, rerank_helper, user_helper
        return ofair


    def __init__(self, rating, training, rerank_helper):
        Reranker.__init__(self, rating, training, rerank_helper, self.fun())


    def entropy(self, labels):
        n_labels = len(labels)
        if n_labels <= 1:
            return 0

        value, counts = np.unique(labels, return_counts=True)
        probs = counts / n_labels
        n_classes = np.count_nonzero(probs)

        if n_classes <= 1:
            return 0

        entropy = -np.sum(np.log2(probs) * probs)
        return entropy,value


    def calculate_weight(self):
        item_feature_df = self.rerank_helper.item_feature_df
        protected = self.rerank_helper.protected

        labels = item_feature_df['feature']
        ent, val = self.entropy(labels)
        weight_dict = {}
        for feature in val:
            if feature in protected:
                weight_dict[feature] = np.sqrt(100 * ent)
            else:
                weight_dict[feature] = np.sqrt(ent)
        self.rerank_helper.weight = weight_dict

        


RESULT_FILE_PATTERN = 'out-(\d+).txt'
INPUT_FILE_PATTERN = 'cv_\d+'


def read_args():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(description='Generic re-ranking script')
    parser.add_argument('conf', help='Name of configuration file')
    parser.add_argument('original', help='Path to original results directory')
    parser.add_argument('result', help='Path to destination results directory')
    parser.add_argument('--max_len', help='The maximum number of items to return in each list', default=10)
    parser.add_argument('--lambda', help='The weight for re-ranking.')
    parser.add_argument('--binary', help='Whether P(\\bar{s)|d) is binary or real-valued', default=True)
    parser.add_argument('--alpha', help='alpha.')
    parser.add_argument('--protected', help='protected feature', default="new")
    parser.add_argument('--method', help='reranking method')

    input_args = parser.parse_args()
    return vars(input_args)


def enumerate_results(result_path):
    pat = re.compile(RESULT_FILE_PATTERN)
    files = [file for file in result_path.iterdir() if pat.match(file.name)]
    files.sort()
    return files


def load_item_features(config, data_path):
    item_feature_file = single_xpath(
        config.get_xml(), '/librec-auto/features/item-feature-file').text
    item_feature_path = data_path / item_feature_file

    if not item_feature_path.exists():
        print("Cannot locate item features. Path: " + item_feature_path)
        return None

    item_feature_df = pd.read_csv(item_feature_path,
                                  names=['itemid', 'feature', 'value'])
    item_feature_df.set_index('itemid', inplace=True)
    return item_feature_df


def output_reranked(reranked_df, dest_results_path, file_path):
    output_file_path = dest_results_path / file_path.name
    print('Reranking for ', output_file_path)
    reranked_df.to_csv(output_file_path, header=False, index=False)


def load_training(split_path, cv_count):
    tr_file_path = split_path / f'cv_{cv_count}' / 'train.txt'

    if not tr_file_path.exists():
        print('Cannot locate training data: ' + str(tr_file_path.absolute()))
        return None

    tr_df = pd.read_csv(tr_file_path, names=['userid', 'itemid', 'score'], sep='\t')

    return tr_df


def execute(rerank_helper, pat, file_path, split_path, dest_results_path):
    tr_df = None

    m = re.match(pat, file_path.name)
    cv_count = m.group(1)
    tr_df = load_training(split_path, cv_count)
    if tr_df is None:
        print("no traning data")
        exit(-1)

    rating_df = pd.read_csv(file_path, names=['userid', 'itemid', 'rating'])

    re_ranker = OFAIR(rating_df, tr_df, rerank_helper)
    re_ranker.calculate_weight()
    reranked_df, rerank_helper = re_ranker.reranker()

    output_reranked(reranked_df, dest_results_path, file_path)


def main():
    args = read_args()
    config = read_config_file(args['conf'], '.')

    original_results_path = Path(args['original'])
    result_files = enumerate_results(original_results_path)

    dest_results_path = Path(args['result'])

    data_dir = single_xpath(config.get_xml(), '/librec-auto/data/data-dir').text

    data_path = Path(data_dir)
    data_path = data_path.resolve()

    item_feature_df = load_item_features(config, data_path)
    if item_feature_df is None:
        exit(-1)

    # item_helper = set_item_helper(item_feature_df)

    # rerank_helper = set_rerank_helper(args, config, item_helper)
    rerank_helper = Rerank_Helper()
    rerank_helper.set_rerank_helper(args, config, item_feature_df)

    split_path = data_path / 'split'
    pat = re.compile(RESULT_FILE_PATTERN)

    method = args['method']

    p = []

    for file_path in result_files:
        p1 = multiprocessing.Process(target=execute, args=(
            rerank_helper, pat, file_path, split_path, dest_results_path))
        p.append(p1)
        p1.start()

    for p1 in p:
        p1.join()


if __name__ == '__main__':
    main()