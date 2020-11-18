# Calibrated recommendation
# Harald Steck. 2018.
    # In <i>Proceedings of the 12th ACM Conference on Recommender Systems</i> (<i>RecSys '18</i>).
    # Association for Computing Machinery, New York, NY, USA, 154–162.
    # DOI:https://doi.org/10.1145/3240323.3240372
# implemented by Nasim Sonboli

import argparse
import os
import re
import pandas as pd
import numpy as np
from librec_auto.core import read_config_file
from pathlib import Path
from librec_auto.core.util.xml_utils import single_xpath


def compute_genre_distribution(item_list, item_feature_matrix):
    return item_feature_matrix.loc[item_list].sum(axis=0) / len(item_list)


def get_item_feature_matrix(feature_df):
    # feature_df.reset_index(inplace=True, drop=False)
    # item_features_matrix = pd.crosstab(feature_df['itemid'], feature_df['feature'])
    item_features_matrix = pd.crosstab(feature_df.index, feature_df['feature'])
    return item_features_matrix


def kullback_leibler_divergence(interact_dist, recommended_dist):
    import numpy as np
    alpha = 0.01  # not really a tuning parameter, it's there to make the computation more numerically stable.
    kl_dive = 0.0
    for i in range(len(interact_dist)):
        # By convention, 0 * ln(0/a) = 0, so we can ignore keys in q that aren't in p
        if interact_dist[i] == 0.0:
            continue
        # if q = recommendationDist and p = interactedDist, q-hat is the adjusted q.
        # given that KL divergence diverges if recommendationDist or q is zero,
        # we instead use q-hat = (1-alpha).q + alpha . p
        recommended_dist[i] = (1 - alpha) * recommended_dist[i] + alpha * interact_dist[i]
        kl_dive += interact_dist[i] * np.log2(interact_dist[i] / recommended_dist[i])

    return kl_dive


def calibrated_reco(userid, recoms_df, training_df, item_features, lam, top_k):

    user_df_rec = recoms_df
    user_df_training = training_df
    interact_dist = compute_genre_distribution(user_df_training['itemid'].tolist(), item_features)

    final_list = []
    reranked_list = []
    for k in range(top_k):  # top_k means choose top k items for the final re-ranking.
        all_sc = []
        for i in user_df_rec['itemid'].tolist():

            kl_div = 0.0
            recommended_dist = compute_genre_distribution(reranked_list + [i], item_features)
            kl_div = kullback_leibler_divergence(interact_dist, recommended_dist)

            t_score = 0.0
            for j in reranked_list + [i]:
                score = user_df_rec[user_df_rec['itemid'] == j]['score'].values[0]
                t_score += score

            sc = (1 - lam) * score - lam * kl_div
            all_sc.append(sc)  # 0.1 0.5 0.2

        sc_asorted = np.argsort(all_sc)[::-1]  # [1, 2, 0]
        top_item = user_df_rec['itemid'].tolist()[sc_asorted[0]]
        top_score = user_df_rec['score'].tolist()[sc_asorted[0]]

        sc_idx = 0
        # if top item already exists in the list, pick the second best item or the third best item, etc.
        while top_item in reranked_list:
            if sc_idx in sc_asorted:
                top_item = user_df_rec['itemid'].tolist()[sc_asorted[sc_idx]]
                top_score = user_df_rec['score'].tolist()[sc_asorted[sc_idx]]
                sc_idx += 1

        reranked_list.append(top_item)
        final_list.append([userid, top_item, top_score])

    final_df = pd.DataFrame(final_list, columns=['userid', 'itemid', 'score'])
    return final_df


def reranker(rating_file, training_file, item_feature_df, binary, top_k, lamb):

    all_user_id = np.unique(rating_file['userid'].to_numpy())
    num_user = len(all_user_id)

    result = []

    item_feat_matrix = get_item_feature_matrix(item_feature_df)

    for i in range(num_user):
        if i%100 == 0:
            print('.', end='')
        # print('list reranked for user #', i)
        userid = all_user_id[i]
        result.append(calibrated_reco(userid, rating_file[rating_file['userid'] == userid].copy(),
                                      training_file[training_file['userid'] == userid].copy(),
                                      item_feat_matrix, lamb, top_k))

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
    # print(args)  # todo need to be deleted
    config = read_config_file(args['conf'], ".")
    original_results_path = Path(args['original'])

    result_files = enumerate_results(original_results_path)
    if len(result_files) == 0:
        print(
            f"calib_rerank: No original results found in {original_results_path}"
        )

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

    split_path = data_path / 'split'
    pat = re.compile(RESULT_FILE_PATTERN)

    for file_path in result_files:
        # reading the training set to compare with the results
        m = re.match(pat, file_path.name)
        cv_count = m.group(1)

        training_df = load_training(split_path, cv_count)
        if training_df is None:
            exit(-1)

        print(f'Load results from {file_path}')  # todo might not be necessary to print this
        # reading the result
        results_df = pd.read_csv(file_path, names=['userid', 'itemid', 'score'])

        reranked_df = reranker(results_df, training_df,
                               item_feature_df, binary,
                               top_k, lamb)

        output_reranked(reranked_df, dest_results_path, file_path)
