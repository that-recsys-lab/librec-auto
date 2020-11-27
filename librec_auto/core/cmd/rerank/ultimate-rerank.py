# ultimate rerank with helpers
# include MMR, FAR
# Ziyue Guo
# Fall 2020

# config example

# <!--		<script lang="python3" src="system">-->
# <!--			<script-name>ultimate-rerank.py</script-name>-->
# <!--			<param name="max_len">10</param>-->

# <!--			<param name="lambda">-->
# <!--				<value>1.0</value>-->
# <!--				<value>0.5</value>-->
# <!--			</param>-->

# <!--			<param name="method">mmr</param>-->

# <!--			<param name="alpha">-->
# <!--				<value>0.01</value>-->
# <!--				<value>0.15</value>-->
# <!--			</param>-->

# <!--			<param name="binary">True</param>-->
# <!--			<param name="protected">new</param>-->
# <!--		</script>-->

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

# helpers

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

    def num_prot(self, items):
        num_prot = [self.is_protected(itemid) for itemid in items].count(True)
        return num_prot


def set_rerank_helper(args, config, item_helper):
    # basic info
    rerank_helper = Rerank_Helper()
    rerank_helper.binary = args['binary'] == 'True'
    rerank_helper.max_len = int(args['max_len'])

    # protected data
    # try: rerank_helper.protected = str(args['protected'])
    try:
        protected = single_xpath(config.get_xml(),
                                 '/librec-auto/metric/protected-feature').text
    except:
        pass

    try:
        rerank_helper.protected_set = get_protected_set(item_helper.item_feature_df, item_helper)
    except:
        pass

    # hyper-parameters
    try:
        rerank_helper.lamb = float(args['lambda'])
    except:
        pass

    try:
        rerank_helper.alpha = float(args['alpha'])
    except:
        pass

    return rerank_helper


class User_Helper():
    profile = None
    score_profile = None
    id = -1
    scaled_rating = None
    item_list = None
    item_so_far = []
    item_so_far_score = []
    tol = None


def set_user_helper(user_id, rating_df, user_profile, rerank_helper):
    user_helper = User_Helper()
    user_helper.id = user_id

    user_rating = rating_df.loc[rating_df["userid"] == user_id, [
        "rating"]].to_numpy()

    scaler = MinMaxScaler()

    user_helper.scaled_rating = scaler.fit_transform(user_rating).flatten()

    user_helper.item_list = rating_df.loc[rating_df["userid"] == user_id, [
        "itemid"]].to_numpy().flatten()

    if user_profile is not None:
        user_helper.profile = user_profile
        user_helper.score_profile = score_prot(user_profile, rerank_helper)

    return user_helper


class Item_Helper():
    item_feature_df = None
    sim_matrix_dic = {}

    def update_sim_matrix_dic(self, index1, index2, binary):

        if index1 in self.sim_matrix_dic:
            if index2 in self.sim_matrix_dic[index1]:
                return self.sim_matrix_dic[index1][index2]

        vec_proj1 = self.item_feature_df.loc[[index1, ]]
        vec_proj2 = self.item_feature_df.loc[[index2, ]]

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


# rerank methods


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


def FAR(rec, item_helper, rerank_helper, user_helper):
    # num_prot = rerank_helper.num_prot(user_helper.item_so_far)
    num_curr = len(user_helper.item_so_far)
    num_remain = len(user_helper.item_list)
    best_score = -1
    scores = []

    for i in range(num_remain):
        item = user_helper.item_list[i]
        score = rec[i]
        if rerank_helper.binary:
            new_score = rescore_binary(item, score, user_helper.item_so_far,
                                       user_helper.score_profile, rerank_helper)
        else:
            new_score = rescore_prop(item, score, user_helper.item_so_far,
                                     user_helper.score_profile, rerank_helper)

        scores.append(new_score)

    return scores, item_helper, rerank_helper, user_helper


def PFAR(rec, item_helper, rerank_helper, user_helper):
    # num_prot = rerank_helper.num_prot(user_helper.item_so_far)
    num_curr = len(user_helper.item_so_far)
    num_remain = len(user_helper.item_list)
    best_score = -1
    scores = []
    user_tol = get_user_tolerance(user_helper.profile, item_helper.item_feature_df, rerank_helper)

    for i in range(num_remain):
        item = user_helper.item_list[i]
        score = rec[i]
        if rerank_helper.binary:
            new_score = rescore_binary(item, score, user_helper.item_so_far,
                                       user_helper.score_profile, rerank_helper, user_tol)
        else:
            new_score = rescore_prop(item, score, user_helper.item_so_far,
                                     user_helper.score_profile, rerank_helper, user_tol)

        scores.append(new_score)

    return scores, item_helper, rerank_helper, user_helper


# functions inside methods


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


def get_user_tolerance(user_profile, item_features, helper):
    # look through the items that the user has rated before
    # look through the item features and save a list of all these feature names in a file
    # call entropy_() function and return the entropy result
    user_items = user_profile['itemid'].tolist()
    if len(user_items) == 0:
        return 0
    return entropy_(item_features.loc[item_features.index.isin(user_items),
                                      'feature'].tolist())


def entropy_(labels, base=None):
    from math import log, e
    """ Computes entropy of label distribution. """
    n_labels = len(labels)
    if n_labels <= 1:
        return 0

    value, counts = np.unique(labels, return_counts=True)
    probs = counts / n_labels
    n_classes = np.count_nonzero(probs)

    if n_classes <= 1:
        return 0
    ent = 0.
    # Compute entropy
    base = e if base is None else base
    for i in probs:
        ent -= i * log(i, base)

    return ent


def get_protected_set(item_features, helper):
    return set((item_features[(item_features['feature'] == helper.protected)
                              & (item_features['value'] == 1)].index).tolist())


def rescore_binary(item, original_score, items_so_far, score_profile, helper, user_tol = None):
    answer = original_score
    div_term = 0

    # If there are both kind of items in the list, no re-ranking happens
    count_prot = helper.num_prot(items_so_far)
    if helper.is_protected(item):
        if count_prot == 0:
            div_term = score_profile
    else:
        if count_prot == len(items_so_far):
            div_term = 1 - score_profile

    if user_tol is None:
        div_term *= (1 - helper.lamb)
        answer *= helper.lamb
        answer += div_term

    else:
        div_term *= helper.lamb
        answer += div_term
        div_term *= user_tol        

    return answer


def rescore_prop(item, original_score, items_so_far, score_profile, helper, user_tol = None):
    answer = original_score

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

    if user_tol is None:
        div_term *= (1 - helper.lamb)
        answer *= helper.lamb
        answer += div_term

    else:
        div_term *= helper.lamb
        answer += div_term
        div_term *= user_tol      
    return answer


def score_prot(user_profile, helper):
    user_items = user_profile['itemid'].tolist()
    if len(user_items) == 0:
        return 0
    return helper.num_prot(user_items) * 1.0 / len(user_items)


# core rerank


def greedy_enhance(rerank_helper, item_helper, user_helper, scoring_function):
    user_helper.item_so_far = []
    item_idx = np.argmax(user_helper.scaled_rating)

    user_helper.item_so_far.append(user_helper.item_list[item_idx])
    num_item = rerank_helper.max_len

    rec = user_helper.scaled_rating.copy()
    user_helper.item_list = np.delete(user_helper.item_list, item_idx)

    all_scores = np.zeros(num_item)
    # all_scores[0] = user_helper.scaled_rating[item_idx] * rerank_helper.lamb
    all_scores[0] = user_helper.scaled_rating[item_idx]
    scaler = MinMaxScaler()

    for k in range(num_item - 1):
        rec = np.delete(rec, item_idx)

        # scoring function
        scores, item_helper, rerank_helper, user_helper = scoring_function(rec, item_helper, rerank_helper, user_helper)

        max_idx = np.argmax(np.array(scores))
        all_scores[k + 1] = scores[max_idx]

        user_helper.item_so_far.append(user_helper.item_list[max_idx])
        user_helper.item_list = np.delete(user_helper.item_list, max_idx)
        item_idx = max_idx

    user_helper.item_so_far_score = list(scaler.fit_transform(all_scores.reshape(-1, 1)).flatten())
    return rerank_helper, item_helper, user_helper


def reranker(rating, training, rerank_helper, item_helper, scoring_function):
    all_user_id = np.unique(rating['userid'].to_numpy())
    num_user = len(all_user_id)

    user, item, score = [], [], []

    for i in range(num_user):

        user_id = all_user_id[i]
        user_profile = None
        
        if training is not None:

            user_profile = training[training['userid'] == user_id]

        user_helper = set_user_helper(user_id, rating, user_profile, rerank_helper)

        rerank_helper, item_helper, user_helper = greedy_enhance(rerank_helper, item_helper, user_helper,
                                                                 scoring_function)

        user += [user_helper.id] * rerank_helper.max_len
        item += user_helper.item_so_far
        score += user_helper.item_so_far_score

    ziplist = list(zip(user, item, score))
    df = pd.DataFrame(ziplist, columns=['Users', 'Items', 'Ratings'])
    return df, rerank_helper, item_helper


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


def match_method(method):
    if method == "mmr": 
        return MMR, False
    elif method == "far": 
        return FAR, True
    elif method == "pfar":
        return PFAR, True
    else:
        print("rerank method not exist")
        return None, None


def execute(rerank_helper, item_helper, scoring_function, profile_flag, pat, file_path, split_path,dest_results_path):
    tr_df = None

    if profile_flag:
        m = re.match(pat, file_path.name)
        cv_count = m.group(1)
        tr_df = load_training(split_path, cv_count)
        if tr_df is None:
            print("no traning data")
            exit(-1)

    rating_df = pd.read_csv(file_path, names=['userid', 'itemid', 'rating'])
    reranked_df, rerank_helper, item_helper = reranker(rating_df, tr_df, rerank_helper, item_helper, scoring_function)
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

    item_helper = set_item_helper(item_feature_df)
    rerank_helper = set_rerank_helper(args, config, item_helper)

    split_path = data_path / 'split'
    pat = re.compile(RESULT_FILE_PATTERN)

    method = args['method']

    scoring_function, profile_flag = match_method(method)

    if scoring_function is None:
        print("rerank method not exist")
        exit(-1)

    p = []

    for file_path in result_files:
        p1 = multiprocessing.Process(target = execute, args=(rerank_helper, item_helper, scoring_function, profile_flag, pat, file_path, split_path,dest_results_path))
        p.append(p1)
        p1.start()

    for p1 in p:
        p1.join()

if __name__ == '__main__':
    main()



