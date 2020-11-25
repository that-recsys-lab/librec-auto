# MMR rerank with helpers
# Ziyue Guo
# Fall 2020


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


class Rerank_Helper():
    # basic info
    binary = True
    max_len = 10

    # protected data
    protected = None
    protected_set = {}

    # hyper-parameter
    lamb = 0.5
    alpha = 0.02

    def is_protected(self, itemid):
        return itemid in self.protected_set
    def protected_count(self, items):
        num_prot = [self.is_protected(itemid) for itemid in items].count(True)
        return num_prot


def set_rerank_helper(args):
    # basic info
    rerank_helper = Rerank_Helper()
    rerank_helper.binary = args['binary'] == 'True'
    rerank_helper.max_len = int(args['max_len'])

    # protected data
    try: rerank_helper.protected = str(args['protected'])
    except: pass

    # hyper-parameters
    try: rerank_helper.lamb = float(args['lambda'])
    except: pass

    try: rerank_helper.alpha = float(args['alpha'])
    except: pass

    return rerank_helper


class User_Helper():
    profile = None
    id = -1
    scaled_rating = None
    item_list = None
    item_so_far = []
    item_so_far_score = []


def set_user_helper(user_id, rating_df):
    user_helper = User_Helper()
    user_helper.id = user_id

    user_rating = rating_df.loc[rating_df["userid"] == user_id, [
            "rating"]].to_numpy()
    
    scaler = MinMaxScaler()

    user_helper.scaled_rating = scaler.fit_transform(user_rating).flatten()

    user_helper.item_list = rating_df.loc[rating_df["userid"] == user_id, [
            "itemid"]].to_numpy().flatten()

    return user_helper


class Item_Helper():
    item_feature_df = None
    sim_matrix_dic = {}

    def update_sim_matrix_dic(self, index1, index2, binary):

        if index1 in self.sim_matrix_dic:
            if index2 in self.sim_matrix_dic[index1]:
                return self.sim_matrix_dic[index1][index2]


        vec_proj1 = self.item_feature_df.loc[[index1,]]
        vec_proj2 = self.item_feature_df.loc[[index2,]]

        joined = pd.concat([vec_proj1, vec_proj2], axis=0)
        pivoted = joined.pivot(columns='feature').fillna(0)

        vec1 = pivoted.loc[index1].to_numpy()
        vec2 = pivoted.loc[index2].to_numpy()
        sim_score = similarity(vec1, vec2, binary)
            
        sim1 = self.sim_matrix_dic.get(index1, {})
        sim1[index2] = sim_score
        self.sim_matrix_dic[index1] = sim1

        sim2 = self.sim_matrix_dic.get(index2, {})
        sim2[index1] = sim_score
        self.sim_matrix_dic[index2] = sim2

        return sim_score


def set_item_helper(item_feature_df):
    item_helper = Item_Helper()
    item_helper.item_feature_df = item_feature_df
    return item_helper


def MMR(rec, item_helper, rerank_helper, user_helper):
    num_remain = len(user_helper.item_list)
    num_curr = len(user_helper.item_so_far)

    sim = np.zeros([num_remain, num_curr])
    sim_max = np.zeros(num_remain)
    
    for i in range(num_remain):
        for j in range(num_curr):
            index1 = user_helper.item_list[i]
            index2 = user_helper.item_so_far[j]
            sim[i][j] = item_helper.update_sim_matrix_dic(index1, index2, rerank_helper.binary)

        sim_max[i] = np.max(sim[i])
    scores = rerank_helper.lamb * rec - (1 - rerank_helper.lamb) * sim_max

    return scores, item_helper, rerank_helper, user_helper


def greedy_enhance(rerank_helper, item_helper, user_helper, scoring_function):
    user_helper.item_so_far = []
    item_idx = np.argmax(user_helper.scaled_rating)
 
    user_helper.item_so_far.append(user_helper.item_list[item_idx])
    num_item = len(user_helper.item_list)

    rec = user_helper.scaled_rating.copy()
    user_helper.item_list = np.delete(user_helper.item_list, item_idx)

    all_scores = np.zeros(num_item)
    all_scores[0] = user_helper.scaled_rating[item_idx] * rerank_helper.lamb
    scaler = MinMaxScaler()

    for k in range(num_item - 1):
        rec = np.delete(rec, item_idx)

        # scoring function
        # scores, item_helper, rerank_helper, user_helper = scoring_function(rec, item_helper, rerank_helper, user_helper)
        scores, item_helper, rerank_helper, user_helper = MMR(rec, item_helper, rerank_helper, user_helper)

        max_idx = np.argmax(scores)
        all_scores[k + 1] = scores[max_idx]
 
        user_helper.item_list = np.delete(user_helper.item_list, max_idx)
        item_idx = max_idx

    user_helper.item_so_far_score = list(scaler.fit_transform(all_scores.reshape(-1, 1)).flatten())
    return rerank_helper, item_helper, user_helper


def reranker(rating, rerank_helper, item_helper, scoring_function):
    all_user_id = np.unique(rating['userid'].to_numpy())
    num_user = len(all_user_id)

    user, item, score = [], [], []

    for i in range(num_user):
        user_id = all_user_id[i]
        user_helper = set_user_helper(user_id, rating)

        rerank_helper, item_helper, user_helper = greedy_enhance(rerank_helper, item_helper, user_helper, scoring_function)
    
        user += [user_helper.id] * rerank_helper.max_len
        item += user_helper.item_so_far
        score += user_helper.item_so_far_score


    ziplist = list(zip(user, item, score))
    df = pd.DataFrame(ziplist, columns=['Users', 'Items', 'Ratings'])
    return df, rerank_helper, item_helper


def similarity(feature1, feature2, binary):
    if binary:
        return np.count_nonzero(np.logical_and(feature1, feature2)) / \
               np.count_nonzero(np.logical_or(feature1, feature2))

    try:
        return 1 - distance.cosine(feature1, feature2)
    except:
        tol = 0.0001
        feature1 = np.append(feature1, tol)
        feature2 = np.append(feature2, tol)
        return 1 - distance.cosine(feature1, feature2)

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
    parser.add_argument('--lambda', help='The weight for re-ranking.')
    parser.add_argument('--binary', help='Whether P(\\bar{s)|d) is binary or real-valued', default=True)

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

    item_helper = set_item_helper(item_feature_df)
    rerank_helper = set_rerank_helper(args)

    scoring_function = 'mmr'

    for file_path in result_files:

        rating_df = pd.read_csv(file_path, names=['userid', 'itemid', 'rating'])
        reranked_df, rerank_helper, item_helper = reranker(rating_df, rerank_helper, item_helper, scoring_function)
        output_reranked(reranked_df, dest_results_path, file_path)


if __name__ == '__main__':
    main()



