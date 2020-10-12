# MMR rerank
# Ziyue Guo
# Fall 2020
# If item's features not found in item_feature_file, let the feature = 'new'
# Not support split cv now

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

    # if method == 'xor':
    #    return 1 - np.sum(np.logical_xor(feature1, feature2)) / len(feature1)

    # if method == 'dot':
    #    return np.mean(feature1 * feature2)


# RB 2020-09-22 Would be (much) faster to pivot the item feature data set up front. Then the
# similarity calculations will be much faster. Better yet would be to build a similarity matrix
# of just the items that are in the result set, and consult that.
def MMR_algorithm(lamb, user_id, item_feature_df, scaled_ratings,
                  user_item_list, scaler, sim_method, top_k):

    current_result = []
    remain_list = user_item_list.copy()
    item_idx = np.argmax(scaled_ratings)
    current_result.append(remain_list[item_idx])
    num_item = len(remain_list)

    if (top_k <= 0 or top_k > num_item):
        top_k = num_item

    if (top_k == 1):
        return user_id, current_result, np.array([scaled_ratings[item_idx]])

    rec = scaled_ratings.copy()
    remain_list = np.delete(remain_list, item_idx)
    all_scores = np.zeros(top_k)
    all_scores[0] = scaled_ratings[item_idx] * lamb

    for k in range(top_k - 1):
        rec = np.delete(rec, item_idx)
        num_remain = len(remain_list)
        num_curr = len(current_result)
        sim = np.zeros([num_remain, num_curr])
        sim_max = np.zeros(num_remain)

        for i in range(num_remain):

            for j in range(num_curr):
                index1 = remain_list[i]
                index2 = current_result[j]

                vec_proj1 = item_feature_df.loc[[
                    index1,
                ]]
                vec_proj2 = item_feature_df.loc[[
                    index2,
                ]]

                joined = pd.concat([vec_proj1, vec_proj2], axis=0)

                pivoted = joined.pivot(columns='feature').fillna(0)

                vec1 = pivoted.loc[index1].to_numpy()
                vec2 = pivoted.loc[index2].to_numpy()
                sim[i][j] = similarity(vec1, vec2, sim_method)

            sim_max[i] = np.max(sim[i])

        scores = lamb * rec - (1 - lamb) * sim_max

        max_idx = np.argmax(scores)
        all_scores[k + 1] = scores[max_idx]
        current_result.append(remain_list[max_idx])
        remain_list = np.delete(remain_list, max_idx)
        item_idx = max_idx

    return [user_id] * top_k, current_result, scaler.fit_transform(
        all_scores.reshape(-1, 1)).flatten()
    # return [user_id] * top_k, current_result, all_scores


def reranker(lamb, rating_file, item_feature_df, binary, top_k=0):

    all_user_id = np.unique(rating_file['userid'].to_numpy())
    num_user = len(all_user_id)

    scaler = MinMaxScaler()
    sim_method = 'jaccard' if binary else 'cosine'

    user = []
    item = []
    score = []

    for i in range(num_user):
        user_id = all_user_id[i]
        user_rating = rating_file.loc[rating_file["userid"] == user_id,
                                      ["rating"]].to_numpy()
        scaled_ratings = scaler.fit_transform(user_rating).flatten()
        user_item_list = rating_file.loc[rating_file["userid"] == user_id,
                                         ["itemid"]].to_numpy().flatten()

        result = MMR_algorithm(lamb, user_id, item_feature_df, scaled_ratings,
                               user_item_list, scaler, sim_method, top_k)

        user = user + [user_id] * top_k
        item = item + list(result[1])
        score = score + list(result[2])

    ziplist = list(zip(user, item, score))
    df = pd.DataFrame(ziplist, columns=['Users', 'Items', 'Ratings'])
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

    data_dir = single_xpath(config.get_xml(),
                            '/librec-auto/data/data-dir').text
    data_path = Path(data_dir)
    data_path = data_path.resolve()

    item_feature_df = load_item_features(config, data_path)
    if item_feature_df is None:
        exit(-1)

    lamb = float(args['lambda'])
    top_k = int(args['max_len'])
    binary = args['binary'] == 'True'

    for file_path in result_files:

        results_df = pd.read_csv(file_path,
                                 names=['userid', 'itemid', 'rating'])
        reranked_df = reranker(lamb, results_df, item_feature_df, binary,
                               top_k)

        output_reranked(reranked_df, dest_results_path, file_path)


if __name__ == '__main__':
    main()
