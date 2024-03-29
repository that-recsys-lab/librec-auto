# Fa*ir rerank
# Ziyue Guo
# Fall 2020
# base on Masoud's code


# rerank config:

# < script
# lang = "python3"
# src = "system" >
# < script - name > fairstar_rerank.py < / script - name >
# < param
# name = "max_len" > 10 < / param >
# < param
# name = "alpha" >
# < value > 0.05 < / value >
# < value > 0.25 < / value >
# < / param >
# < param
# name = "binary" > True < / param >
# < param
# name = "protected" > "new" < / param >
# < / script >

import numpy as np
import pandas as pd
from scipy.spatial import distance
from sklearn.preprocessing import MinMaxScaler
import argparse
from librec_auto.core import read_config_file
from librec_auto.core.util.xml_utils import single_xpath
import os
import re
from pathlib import Path
import fairsearchcore as fsc
from fairsearchcore import re_ranker
import warnings
warnings.filterwarnings('ignore')

def fair_top_k(k, protected_candidates, non_protected_candidates,p_score,n_score, proportion):

    result = []
    countProtected = 0

    idxProtected = 0
    idxNonProtected = 0

    for i in range(k):
        if idxProtected >= len(protected_candidates) and idxNonProtected >= len(non_protected_candidates):
            # no more candidates available, return list shorter than k
            # print("A")
            return result
        if idxProtected >= len(protected_candidates):
            # no more protected candidates available, take non-protected instead
            result.append(non_protected_candidates[idxNonProtected])
            idxNonProtected += 1
            # print("B")

        elif idxNonProtected >= len(non_protected_candidates):
            # no more non-protected candidates available, take protected instead
            result.append(protected_candidates[idxProtected])
            idxProtected += 1
            countProtected += 1
            # print("C")
        elif countProtected < proportion * k:
            # add a protected candidate
            result.append(protected_candidates[idxProtected])
            idxProtected += 1
            countProtected += 1
            # print("D")
        else:
            # find the best candidate available
            # print("E")
            if p_score[idxProtected] >= n_score[idxNonProtected]:
                # the best is a protected one
                result.append(protected_candidates[idxProtected])
                idxProtected += 1
                countProtected += 1
            else:
                # the best is a non-protected one
                result.append(non_protected_candidates[idxNonProtected])
                idxNonProtected += 1

    return result 

class FairStarHelper():
    item_feature_df = None
    binary = True
    
    alpha = 0
    prop = 0
    max_len = 0

    protected = None
    protected_set = {}
    unprotected_set = {}

    def is_protected(self, itemid):
        return itemid in self.protected_set
    def protected_count(self, items):
        num_prot = [self.is_protected(itemid) for itemid in items].count(True)
        return num_prot

def set_helper(alpha, max_len, binary, protected, item_feature_df):
    items = item_feature_df["itemid"].to_numpy()
    helper = FairStarHelper()
    helper.protected = protected
    helper.protected_set = get_protected_set(item_feature_df, helper)
    helper.alpha = alpha
    helper.max_len = max_len
    helper.binary = binary
    helper.prop = protected_prop(helper, items)
    return helper

def get_protected_set(item_features, helper):
    if isinstance(helper.protected, str):
        return set((item_features[(item_features['feature'] == helper.protected)
                              & (item_features['value'] == 1)].itemid).tolist())
    else:
        for p in helper.protected:
            print(p)
            return set((item_features[(item_features['feature'] == p)
                              & (item_features['value'] == 1)].itemid).tolist())

def protected_prop(helper, items):
    return helper.protected_count(items) / len(items)

def generate_fairstar(helper):
    max_len = helper.max_len
    p = helper.prop
    alpha = helper.alpha
    print("alpha: ", alpha)
    fair = fsc.Fair(max_len, p, alpha)
    return fair

def rerank(user_rating_df, fair, helper):
    all_user_id = np.unique(user_rating_df['userid'].to_numpy())
    num_user = len(all_user_id)
    scaler = MinMaxScaler()

    user_id = []
    reranked_id = []
    reranked_score = []
    
    for user in all_user_id:

        user_rating = user_rating_df.loc[user_rating_df["userid"] == user, ["rating"]].to_numpy()
        scaled_ratings = scaler.fit_transform(user_rating).flatten()
        unfair_list = []
        items = user_rating_df.loc[user_rating_df["userid"] == user, ["itemid"]].to_numpy().flatten()
        # print
        # print(help)
        protected_candidates = []
        non_protected_candidates = []

        p_score = []
        n_score = []
        # print(user)
        for i in range(len(items)):

            item = items[i]
            score = (scaled_ratings[i] * 100)
            # unfair_list.append(fsc.models.FairScoreDoc(item,score, False if item not in helper.protected_set else True))
            if item not in helper.protected_set:
                non_protected_candidates.append(item)
                n_score.append(score)
            else:
                protected_candidates.append(item)
                p_score.append(score)
            # print(item, score, False if item not in helper.protected_set else True)

        # fair.is_fair(unfair_list)
        re_ranked = fair_top_k(helper.max_len, protected_candidates, non_protected_candidates, p_score, n_score, helper.alpha)
        # print(re_ranked)
        # print([(i.id, i.score) for i in re_ranked])
        # print()
        for j in range(helper.max_len):
            user_id.append(user)
            reranked_id.append(re_ranked[j])
            reranked_score.append((100 - j) / 100)
    
    ziplist = list(zip(user_id, reranked_id, reranked_score))
    df = pd.DataFrame(ziplist, columns=['userid', 'itemid', 'rating'])
    return df

RESULT_FILE_PATTERN = 'out-\d+.txt'

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
    parser.add_argument('--alpha', help='alpha.')
    parser.add_argument('--binary', help='Whether P(\\bar{s)|d) is binary or real-valued', default=True)
    parser.add_argument('--protected_feature', help='protected feature')
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
        print("Cannot locate item features. Path: " + str(item_feature_path))
        return None

    item_feature_df = pd.read_csv(item_feature_path,
                                      names=['itemid', 'feature', 'value'])
    #item_feature_df.set_index('itemid', inplace=True)
    return item_feature_df

def output_reranked(reranked_df, dest_results_path, file_path):
    output_file_path = dest_results_path / file_path.name
    print('Reranking for ', output_file_path)
    reranked_df.to_csv(output_file_path, header=False, index=False)

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
    config = read_config_file(args['conf'], '.')

    original_results_path = Path(args['original'])
    result_files = enumerate_results(original_results_path)

    dest_results_path = Path(args['result'])

    data_dir = single_xpath(config.get_xml(), '/librec-auto/data/data-dir').text

    data_path = Path(data_dir)
    data_path = data_path.resolve()

    item_feature_df = load_item_features(config, data_path)

    # protected = single_xpath(config.get_xml(), '/librec-auto/metric/protected-feature').text


    if item_feature_df is None:
        exit(-1)

    alpha = float(args['alpha'])
    max_len = int(args['max_len'])
    binary = args['binary'] == 'True'
    protected = str(args['protected_feature'])

    helper = set_helper(alpha, max_len, binary, protected, item_feature_df)

    for file_path in result_files:

        results_df = pd.read_csv(file_path, names=['userid', 'itemid', 'rating'])

        fair = None
        reranked_df = rerank(results_df, fair, helper)

        output_reranked(reranked_df, dest_results_path, file_path)


if __name__ == '__main__':
     main()
