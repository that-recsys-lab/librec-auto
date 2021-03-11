
# # Opportunistic Multi-aspect Fairness through Personalized Re-ranking.
    # Nasim Sonboli, Farzad Eskandanian, Robin Burke, Weiwen Liu, and Bamshad Mobasher. 2020.
    # In <i>Proceedings of the 28th ACM Conference on User Modeling, Adaptation and Personalization</i> (<i>UMAP '20</i>).
    # Association for Computing Machinery, New York, NY, USA, 239–247. DOI:https://doi.org/10.1145/3340631.3394846
# implemented by Nasim Sonboli

import argparse
import os
import re
import pandas as pd
import numpy as np
import sklearn
from scipy.spatial import distance
from sklearn.preprocessing import MinMaxScaler
from librec_auto.core import read_config_file
from pathlib import Path
from librec_auto.core.util.xml_utils import single_xpath

class FarHelper:
    item_feature_df = None
    protected = None
    lam = 0
    max_length = 10
    binary = True
    protected_set = {}

    def is_protected(self, itemid):
        return itemid in self.protected_set

    def num_prot(self, items):
        num_prot = [self.is_protected(itemid) for itemid in items].count(True)
        return num_prot


# Caches the protected items for quicker lookup
def get_protected_set(item_features, helper):
    return set((item_features[(item_features['feature'] == helper.protected)
                              & (item_features['value'] == 1)].index).tolist())


def setup_helper(args, config, item_feature_df):
    protected = single_xpath(config.get_xml(),
                             '/librec-auto/metric/protected-feature').text

    helper = FarHelper()
    helper.protected = protected
    helper.protected_set = get_protected_set(item_feature_df, helper)
    helper.lam = float(args['lambda'])
    helper.max_length = int(args['max_len'])
    helper.binary = args['binary'] == 'True'
    return helper


# todo debug here and also change, what is this tolerance 0.001????
def similarity(feature1, feature2, method):
    if method == 'jaccard':
        return np.count_nonzero(np.logical_and(feature1, feature2)) / \
               np.count_nonzero(np.logical_or(feature1, feature2))

    if method == 'cosine':
        try:
            return 1 - distance.cosine(feature1, feature2)
        except:
            method = 'cosine_advance'

    if method == 'cosine_advance':
        tol = 0.0001
        feature1 = np.append(feature1, tol)
        feature2 = np.append(feature2, tol)
        return 1 - distance.cosine(feature1, feature2)


def generate_user_entropy_matrix():
    pass

def compute_entropy():
    pass


def ofair(userid, rating_file, item_features, scaler, lamb, top_k, w=None):

    # making sure that the scores are between zero and one across all users, similar to cosine score
    # otherwise how do we combine these two different scores
    user_ratings = rating_file["rating"].to_numpy()
    scaled_ratings = scaler.fit_transform(user_ratings).flatten()
    user_item_list = rating_file["itemid"].to_numpy().flatten()

    if w is not None:
        dists = sklearn.metrics.pairwise_distances(np.sqrt(w) * item_features.loc[user_item_list],
                                                   metric='cosine', n_jobs=1)
    else:
        dists = sklearn.metrics.pairwise_distances(item_features.loc[user_item_list],
                                                   metric='cosine', n_jobs=1)

    c = 0
    s = []
    for k in range(top_k):  # top_k means choose top k items for the final re-ranking.
        all_sc = []
        # iterate through the items that are recommended to user.
        # we choose the first 200 items.
        for rec_idx in range(len(user_item_list)):
            p2 = 0
            for j in s:
                try:
                    # comparing item features
                    # the distances  of all items was calculated before for efficiency
                    p = 1 - dists[rec_idx, user_item_list.tolist().index(j)]
                    p2 += p
                except KeyError as e:
                    pass

                    # mmr objective function
            # sc = lam * (1 - distance.cosine(u, items[i])) - (1-lam) * p2
            r = scaled_ratings[rec_idx]

            # get the index of an itemid and get the rating related to it
            sc = lamb * r - (1 - lamb) * p2

            # find the index of a user id and then go to that index to retrieve the score
            all_sc.append(sc)  # 0.1 0.5 0.2

        sc_asorted = np.argsort(all_sc)[::-1]  # [1, 2, 0]
        sc_idx = 0
        top_item = user_item_list[sc_asorted[0]]

        # if top item already exists in the list, pick the second best item or the third best item
        while top_item in s:
            top_item = user_item_list[sc_asorted[sc_idx]]
            sc_idx += 1
        s.append(top_item)

    top_ratings = [user_ratings[list(user_item_list).index(i)] for i in s]

    return userid, s, top_ratings


def reranker(rating_file, item_feature_df, binary, top_k, lamb, w=None):

    all_user_id = np.unique(rating_file['userid'].to_numpy())
    num_user = len(all_user_id)

    scaler = MinMaxScaler()
    sim_method = 'jaccard' if binary else 'cosine'

    result = []

    # item_feat_matrix = get_item_feature_matrix(item_feature_df)

    for i in range(num_user):
        # if i%100 == 0:
        #     print('.', end='')
        # print('list reranked for user #', i)
        userid = all_user_id[i]
        result.append(ofair(userid, rating_file[rating_file['userid'] == userid].copy(),
                            item_feature_df, scaler, lamb, top_k, w))  # todo give the weights here

    rr_df = pd.concat(result)
    return rr_df


def read_args():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(description='Generic re-ranking script')
    parser.add_argument('conf', help='Name of configuration file')
    parser.add_argument('original', help='Path to original results directory')
    parser.add_argument('result', help='Path to destination results directory')
    parser.add_argument(
        '--max_len',
        help='The maximum number of items to return in each list',
        default=10)
    parser.add_argument('--lambda', help='The weight for re-ranking.')
    parser.add_argument('--binary',
                        help='Whether P(\\bar{s)|d) is binary or real-valued',
                        default=True)

    input_args = parser.parse_args()
    return vars(input_args)


RESULT_FILE_PATTERN = 'out-(\d+).txt'
# INPUT_FILE_PATTERN = 'cv_\d+'

def enumerate_results(result_path):
    pat = re.compile(RESULT_FILE_PATTERN)
    # pat = re.compile(a_pattern)
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


def load_training(split_path, cv_count):
    tr_file_path = split_path / f'cv_{cv_count}' / 'train.txt'
    # tr_file_path = Path(tr_file_path)

    if not tr_file_path.exists():
        print('Cannot locate the training data: ' + str(tr_file_path.absolute()))
        return None

    tr_df = pd.read_csv(tr_file_path,
                        names=['userid', 'itemid', 'score'],
                        sep='\t')

    return tr_df

def output_reranked(reranked_df, dest_results_path, file_path):
    output_file_path = dest_results_path / file_path.name
    print('Reranking for ', output_file_path)
    reranked_df.to_csv(output_file_path, header=False, index=False)


if __name__ == '__main__':
    args = read_args()
    config = read_config_file(args['conf'], ".")
    original_results_path = Path(args['original'])

    result_files = enumerate_results(original_results_path)
    if len(result_files) == 0:
        print(
            f"calibrated reco_rerank: No original results found in {original_results_path}"
        )

    dest_results_path = Path(args['result'])

    data_dir = single_xpath(config.get_xml(), '/librec-auto/data/data-dir').text

    data_path = Path(data_dir)
    data_path = data_path.resolve()

    item_feature_df = load_item_features(config, data_path)
    if item_feature_df is None:
        exit(-1)

    lamb = float(args['lambda'])
    top_k = int(args['max_len'])
    binary = args['binary'] == 'True'
    # sim_matrix_dic = {}  # todo why do we need this?


    # split_path = data_path / 'split'
    # pat = re.compile(RESULT_FILE_PATTERN)

    for file_path in result_files:
        # reading the training set to compare with the results
        # m = re.match(pat, file_path.name)
        # cv_count = m.group(1)
        #
        # training_df = load_training(split_path, cv_count)
        # if training_df is None:
        #     exit(-1)

        # print(f'Load results from {file_path}')  # todo might not be necessary to print this
        # reading the result
        results_df = pd.read_csv(file_path, names=['userid', 'itemid', 'score'])

        # todo passing an empty dictionary to the function? sim_matrix_dict - but why?
        # reranked_df, sim_matrix_dic = reranker(results_df, item_feature_df,
        #                                        sim_matrix_dic, binary,
        #                                        top_k, lamb)

        reranked_df, sim_matrix_dic = reranker(results_df, item_feature_df, binary, top_k, lamb) # pass weights in here

        output_reranked(reranked_df, dest_results_path, file_path)
