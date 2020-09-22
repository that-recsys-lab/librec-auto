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
from librec_auto import read_config_file
import os
import re
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


def Similarity(feature1, feature2, method):
    if method == 'jaccard':
        if len(feature1) == 0:
            feature1 = ['new']
        if len(feature2) == 0:
            feature2 = ['new']
        set1 = set(feature1[0])
        set2 = set(feature2[0])
        return len(set1.intersection(set2)) / len(set1.union(set2))

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


def MMR_algorithm(lamb, user_id, item_feature_df, scaled_ratings, user_item_list, scaler, sim_method, top_k):
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
                feature1 = item_feature_df[item_feature_df['Item_ID'] == remain_list[i]].to_numpy().flatten()[1:]
                feature2 = item_feature_df[item_feature_df['Item_ID'] == current_result[j]].to_numpy().flatten()[1:]
                sim[i][j] = Similarity(feature1, feature2, sim_method)

            sim_max[i] = np.max(sim[i])

        scores = lamb * rec - (1 - lamb) * sim_max

        max_idx = np.argmax(scores)
        all_scores[k + 1] = scores[max_idx]
        current_result.append(remain_list[max_idx])
        remain_list = np.delete(remain_list, max_idx)
        item_idx = max_idx

    return [user_id] * top_k, current_result, scaler.fit_transform(all_scores.reshape(-1, 1)).flatten()
    # return [user_id] * top_k, current_result, all_scores


def reranker(lamb, rating_path, feature_filepath, binary, top_k=0):
    rating_file = pd.read_csv(rating_path, sep=",", names=[
        "user", "item", "rating"])

    item_feature_df = pd.read_csv(feature_filepath, sep=",", names=[
        "Item_ID", "feature1", "feature2"])

    all_user_id = np.unique(rating_file['user'].to_numpy())
    num_user = len(all_user_id)

    scaler = MinMaxScaler()
    sim_method = 'jaccard' if binary else 'cosine'

    user = []
    item = []
    score = []

    for i in range(num_user):
        user_id = all_user_id[i]
        user_rating = rating_file.loc[rating_file["user"] == user_id, [
            "rating"]].to_numpy()
        scaled_ratings = scaler.fit_transform(user_rating).flatten()
        user_item_list = rating_file.loc[rating_file["user"] == user_id, [
            "item"]].to_numpy().flatten()

        result = MMR_algorithm(
            lamb, user_id, item_feature_df, scaled_ratings, user_item_list, scaler, sim_method, top_k)

        user = user + [user_id] * top_k
        item = item + list(result[1])
        score = score + list(result[2])

    ziplist = list(zip(user, item, score))
    df = pd.DataFrame(ziplist, columns=['Users', 'Items', 'Ratings'])
    return df



RESULT_FILE_PATTERN = 'out-\d+.txt'
INPUT_FILE_PATTERN = 'cv_\d+'

def read_args():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(description='Generic re-ranking script')
    parser.add_argument('conf', help='Name of configuration file')
    parser.add_argument('target', help='Experiment target')
    parser.add_argument('original', help='Path to original results directory')
    parser.add_argument('result', help='Path to destination results directory')
    parser.add_argument('--max_len', help='The maximum number of items to return in each list', default=10)
    parser.add_argument('--lambda', help='The weight for re-ranking.')
    parser.add_argument('--binary', help='Whether P(\\bar{s)|d) is binary or real-valued', default=True)

    input_args = parser.parse_args()
    return vars(input_args)


def enumerate_results(result_path):
    files = os.listdir(result_path)
    pat = re.compile(RESULT_FILE_PATTERN)
    return [file for file in files if pat.match(file)]


def main():
    args = read_args()
    config = read_config_file(args['conf'], args['target'])
    result_files = enumerate_results(args['original'])

    split_path = config.get_files().get_split_path()

    data_dir = config.get_prop_dict()['dfs.data.dir'] 
    item_feature_file = config.get_prop_dict()['data.itemfeature.path']
    protected = config.get_prop_dict()['data.protected.feature']

    item_feature_path = Path(data_dir) / item_feature_file

    if not item_feature_path.exists():
        print("Cannot locate item features. Path: " + item_feature_path)
        exit(-1)

    lamb = float(args['lambda'])
    top_k = int(args['max_len'])
    binary = args['binary'] == 'True'

    for file_name in result_files:
        input_file_path = Path(args['original'] + '/' + file_name)

        cv_path = str(split_path) + '/cv_' + re.findall('\d+', file_name)[0] + '/train.txt'
        tr_file_path = Path(cv_path)

        if not tr_file_path.exists():
            print('Cannot locate training data: ' + tr_file_path)
            exit(-1)

        if input_file_path.exists():
            reranked_df = reranker(lamb, input_file_path, item_feature_path, binary, top_k)

            output_file_path = Path(args['result'] + '/' + file_name)
            print('Reranking for ', output_file_path)
            reranked_df.to_csv(output_file_path, header=None, index=False)



if __name__ == '__main__':
    main()
