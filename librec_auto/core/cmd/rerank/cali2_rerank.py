# Calibrated recommendation
# Harald Steck. 2018.
# In <i>Proceedings of the 12th ACM Conference on Recommender Systems</i> (<i>RecSys '18</i>).
# Association for Computing Machinery, New York, NY, USA, 154–162.
# DOI:https://doi.org/10.1145/3240323.3240372
# implemented by Nasim Sonboli
# reimplemented by Ziyue Guo, 27 times faster than Nasim's version

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


class Rerank_Helper():
    def __init__(self):
        # basic info
        self.binary = True
        self.max_len = 10

        # protected data
        self.protected = None
        self.protected_set = {}

        # hyper-parameter
        self.lamb = 0.5
        self.alpha = 0.02

        # item
        self.item_feature_df = None
        self.sim_matrix_dic = {}
        self.item_feature_matrix = None

    def set_rerank_helper(self, args, config, item_feature_df):
        # basic info
        self.binary = args['binary'] == 'True'
        self.max_len = int(args['max_len'])
        self.item_feature_df = item_feature_df
        self.item_feature_matrix = self.item_feature_matrix = pd.crosstab(item_feature_df.index, item_feature_df['feature'])

        # protected data
        # try: rerank_helper.protected = str(args['protected'])
        try:
            self.protected = single_xpath(config.get_xml(),
                                          '/librec-auto/metric/protected-feature').text
        except:
            pass

        try:
            self.protected_set = self.get_protected_set()
        except:
            pass

        # hyper-parameters
        try:
            self.lamb = float(args['lambda'])
        except:
            pass

        try:
            self.alpha = float(args['alpha'])
        except:
            pass

    def is_protected(self, itemid):
        return itemid in self.protected_set

    def num_prot(self, items):
        num_prot = [self.is_protected(itemid) for itemid in items].count(True)
        return num_prot

    def get_protected_set(self):
        return set((self.item_features[(self.item_features['feature'] == self.protected)
                                       & (self.item_features['value'] == 1)].index).tolist())

    def similarity(self, feature1, feature2, binary):
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
        sim_score = self.similarity(vec1, vec2, binary)

        sim1 = self.sim_matrix_dic.get(index1, {})
        sim1[index2] = sim_score
        self.sim_matrix_dic[index1] = sim1

        sim2 = self.sim_matrix_dic.get(index2, {})
        sim2[index1] = sim_score
        self.sim_matrix_dic[index2] = sim2

        return sim_score

    def compute_genre_distribution(self, item_list):
        return self.item_feature_matrix.loc[item_list].sum(axis=0) / len(item_list)


class User_Helper():
    def __init__(self):
        self.profile = None
        self.score_profile = None
        self.id = -1
        self.scaled_rating = None
        self.item_list = None
        self.item_so_far = []
        self.item_so_far_score = []
        self.tol = None
        self.distribution = None
        self.rec_dist = 0

    def set_user_helper(self, user_id, rating_df, user_profile, rerank_helper):
        user_helper = User_Helper()
        self.id = user_id

        user_rating = rating_df.loc[rating_df["userid"] == user_id, [
            "rating"]].to_numpy().transpose()[0]

        # scaler = MinMaxScaler()

        # self.scaled_rating = scaler.fit_transform(user_rating).flatten()
        self.scaled_rating = user_rating

        self.item_list = rating_df.loc[rating_df["userid"] == user_id, [
            "itemid"]].to_numpy().flatten()

        if user_profile is not None:
            self.profile = user_profile
            self.score_profile = self.score_prot(user_profile, rerank_helper)

    def score_prot(self, user_profile, rerank_helper):
        user_items = user_profile['itemid'].tolist()
        if len(user_items) == 0:
            return 0
        return rerank_helper.num_prot(user_items) * 1.0 / len(user_items)


class Reranker():

    def __init__(self, rating, training, rerank_helper, scoring_function):
        self.rating = rating
        self.training = training
        self.rerank_helper = rerank_helper
        # self.item_helper = item_helper
        self.user_helper = User_Helper()

        # self.scoring_function = self.fun()
        self.scoring_function = scoring_function

    def reranker(self):
        all_user_id = np.unique(self.rating['userid'].to_numpy())
        num_user = len(all_user_id)

        user, item, score = [], [], []

        for i in range(num_user):

            user_id = all_user_id[i]
            user_profile = None

            if self.training is not None:
                user_profile = self.training[self.training['userid'] == user_id]

            # user_helper = set_user_helper(user_id, rating, user_profile, rerank_helper)
            self.user_helper = User_Helper()
            self.user_helper.set_user_helper(user_id, self.rating, user_profile, self.rerank_helper)

            self.greedy_enhance()

            user += [self.user_helper.id] * self.rerank_helper.max_len
            item += self.user_helper.item_so_far
            score += self.user_helper.item_so_far_score

        ziplist = list(zip(user, item, score))
        df = pd.DataFrame(ziplist, columns=['Users', 'Items', 'Ratings'])
        return df, self.rerank_helper

    def greedy_enhance(self):
        self.user_helper.item_so_far = []
        num_item = self.rerank_helper.max_len
        rec = self.user_helper.scaled_rating.copy()
        all_scores = np.zeros(num_item)

        for k in range(num_item):
            # scoring function
            scores, self.rerank_helper, self.user_helper = self.scoring_function(rec, self.rerank_helper,
                                                                                 self.user_helper)

            max_idx = np.argmax(np.array(scores))
            all_scores[k] = scores[max_idx]

            self.user_helper.item_so_far.append(self.user_helper.item_list[max_idx])
            self.user_helper.item_list = np.delete(self.user_helper.item_list, max_idx)

            rec = np.delete(rec, max_idx)

        self.user_helper.item_so_far_score = list(all_scores)


class CALI(Reranker):
    def fun(self):
        def compute_genre_distribution(item_list, item_feature_matrix):
            m = (item_feature_matrix.loc[item_list]).to_numpy()
            return np.sum(m, axis=0)

        def cali(rec, rerank_helper: Rerank_Helper, user_helper: User_Helper):
            num_remain = len(user_helper.item_list)
            num_curr = len(user_helper.item_so_far) + 1.0

            user_profile_list = user_helper.profile['itemid'].tolist()
            interact_dist = compute_genre_distribution(user_profile_list, rerank_helper.item_feature_matrix)
            interact = np.array(interact_dist)
            ind = np.where(interact != 0)[0]
            interact_m = np.tile(interact[ind], (num_remain, 1)) / len(user_profile_list)

            recommended_m = np.empty([num_remain, len(ind)])

            for i in range(num_remain):
                recommended_dist = compute_genre_distribution(
                     user_helper.item_so_far + [user_helper.item_list[i]], rerank_helper.item_feature_matrix)
                recommended_m[i] = np.array(recommended_dist)[ind]

            alpha = 0.01
            recommended_m /= num_curr
            recommended_m = (1 - alpha) * recommended_m + alpha * interact_m

            kl_div = np.sum(interact_m * np.log2(interact_m / recommended_m), axis=1)

            scores = (1 - rerank_helper.lamb) * rec - rerank_helper.lamb * kl_div

            return scores, rerank_helper, user_helper

        return cali

    def __init__(self, rating, training, rerank_helper):
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


# def execute(rerank_helper, item_helper, scoring_function, profile_flag, pat, file_path, split_path, dest_results_path):
def execute(rerank_helper, pat, file_path, split_path, dest_results_path):
    tr_df = None

    m = re.match(pat, file_path.name)
    cv_count = m.group(1)
    tr_df = load_training(split_path, cv_count)
    if tr_df is None:
        print("no traning data")
        exit(-1)

    rating_df = pd.read_csv(file_path, names=['userid', 'itemid', 'rating'])

    re_ranker = CALI(rating_df, tr_df, rerank_helper)

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