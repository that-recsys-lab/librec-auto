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

class FAR(Reranker):
    def fun(self):
        def rescore_binary(item, original_score, items_so_far, score_profile, helper):
            answer = original_score
            if helper.lamb == 0.0: # Ignoring the diversity term
                return answer

            div_term = 0

            # If there are both kind of items in the list, no re-ranking happens
            count_prot = helper.num_prot(items_so_far)
            if helper.is_protected(item):
                if count_prot == 0:
                    div_term = score_profile
            else:
                if count_prot == len(items_so_far):
                    div_term = 1 - score_profile

            div_term *= helper.lamb
            answer *= (1 - helper.lamb)
            answer += div_term

            return answer

        def rescore_prop(item, original_score, items_so_far, score_profile, helper):
            answer = original_score
            if helper.lamb == 0.0: # Ignoring the diversity term
                return answer

            count_prot = helper.num_prot(items_so_far)
            count_items = len(items_so_far)
            if count_items == 0:
                div_term = score_profile
            else:
                if helper.is_protected(item):
                    div_term = score_profile
                    div_term *= 1 - count_prot / count_items
                else:
                    div_term = (1 - score_profile)
                    div_term *= count_prot / count_items

            div_term *= helper.lamb
            answer *= (1 - helper.lamb)
            answer += div_term
            return answer

        def far(rec, rerank_helper, user_helper):

            num_curr = len(user_helper.item_so_far)
            num_remain = len(user_helper.item_list)
            best_score = -1
            scores = []
            # print("num remain", num_remain)
            # print(rerank_helper.protected_set)
            for i in range(num_remain):
                item = user_helper.item_list[i]
                score = rec[i]
                if rerank_helper.binary:
                    new_score = rescore_binary(item, score, user_helper.item_so_far,
                                            user_helper.score_profile, rerank_helper)
                else:
                    new_score = rescore_prop(item, score, user_helper.item_so_far,
                                            0.5, rerank_helper)

                # if new_score != score:
                #     # if new_score != 0:
                #     print("{} -- item {}: {} -> {}".format(rerank_helper.is_protected(item),item, score, new_score))  
                    # pass
                scores.append(new_score)
            # print("scores", len(scores))    
            return scores, rerank_helper, user_helper
        return far

    def __init__(self, rating, training, rerank_helper, protected = None):
        Reranker.__init__(self, rating, training, rerank_helper, self.fun())


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
    parser.add_argument('--lambda', help='The weight for re-ranking. Higher lambda = more diversity.')
    parser.add_argument('--binary', help='Whether P(\\bar{s)|d) is binary or real-valued', default=True)
    parser.add_argument('--alpha', help='alpha.')
    parser.add_argument('--protected_feature', help='protected feature')
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

#def execute(rerank_helper, item_helper, scoring_function, profile_flag, pat, file_path, split_path, dest_results_path):
def execute(rerank_helper, pat, file_path, split_path, dest_results_path):
    tr_df = None


    m = re.match(pat, file_path.name)
    cv_count = m.group(1)
    tr_df = load_training(split_path, cv_count)
    if tr_df is None:
        print("no training data")
        exit(-1)

    rating_df = pd.read_csv(file_path, names=['userid', 'itemid', 'rating'])

    re_ranker = FAR(rating_df, tr_df, rerank_helper)

    reranked_df, rerank_helper = re_ranker.reranker()

    output_reranked(reranked_df, dest_results_path, file_path)

def check_percentage(item_feature_df):
    store_countries = {}
    total = 0
    for i in range(len(item_feature_df)):
        if "COUNTRY" in item_feature_df.iloc[i]['feature']:
            if item_feature_df.iloc[i]['feature'] not in store_countries:
                store_countries[item_feature_df.iloc[i]['feature']] = 0
            else:
                store_countries[item_feature_df.iloc[i]['feature']] += 1

            total += 1

    for key in store_countries:
        store_countries[key] = store_countries[key]/total

    store_underrepresented = []

    for key in store_countries:
        if store_countries[key] <= 0.01:
            store_underrepresented.append(key)

    return store_underrepresented

def main():
    args = read_args()
    # print(args)
    print("h")
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

    #item_helper = set_item_helper(item_feature_df)

    #rerank_helper = set_rerank_helper(args, config, item_helper)
    protected = str(args['protected_feature'])

    rerank_helper = Rerank_Helper()
    rerank_helper.set_rerank_helper(args, config, item_feature_df, protected)

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


