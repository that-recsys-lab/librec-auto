# FAR rerank
# Based on W. Liu, R. Burke, Personalizing Fairness-aware Re-ranking

import argparse
import os
import re
import pandas as pd
import numpy
from librec_auto import read_config_file
from pathlib import Path
from librec_auto.cmd.rerank.calibrated_common_funcs import *

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
def get_protected_set(item_features):
    return set((item_features[(item_features['feature']=='foo') & (item_features['value']==1)].index).tolist())

#def is_protected(itemid):
#    item_entry = item_feature_df.loc[itemid]
#    prot_item = item_entry[(item_entry['feature']==protected) & (item_entry['value']==1)]
#    return type(prot_item) == numpy.int64

# def num_prot(items):
#     num_prot = [is_protected(itemid) for itemid in items].count(True)
#     return num_prot

def score_prot(user_profile, helper):
    user_items = user_profile['itemid'].tolist()
    if len(user_items)==0:
        return 0
    return helper.num_prot(user_items) / len(user_items)

def rescore_binary(item, original_score, items_so_far, score_profile, helper):
    answer = original_score
    div_term = 0

    # If there are both kind of items in the list, no re-ranking happens
    count_prot = helper.num_prot(items_so_far)
    if helper.is_protected(item):
        if count_prot==0:
            div_term = score_profile
    else:
        if count_prot == len(items_so_far):
            div_term = 1 - score_profile

    div_term *= helper.lam
    answer += div_term
    return answer

# Not in the original paper, but treats the P(\\bar{s)|d) as real-valued
# See Abdollahpouri, Burke, and Mobasher. Managing popularity bias in recommender systems with personalized re-ranking. 2019
def rescore_prop(item, original_score, items_so_far, score_profile, helper):
    answer = original_score
    div_term = 0

    # If there are both kind of items in the list, no re-ranking happens
    count_prot = helper.num_prot(items_so_far)
    count_items = len(items_so_far)
    if helper.is_protected(item):
        div_term = score_profile
        div_term *= 1 - count_prot / count_items
    else:
        div_term = (1 - score_profile)
        div_term *= count_prot / count_items

    div_term *= helper.lam
    answer += div_term
    return answer


def pick_best(user_recs, user_profile, items_so_far, helper):
    best_item = None
    best_score = -1
    score_profile = score_prot(user_profile, helper)

    for _, _, item, score in user_recs.itertuples():
        if helper.binary:
            new_score = rescore_binary(item, score, items_so_far, score_profile, helper)
        else:
            new_score = rescore_prop(item, score, items_so_far, score_profile, helper)
        if new_score > best_score:
            best_item = item
            best_score = new_score

    return (best_item, best_score)

def rerank(userid, user_recs_df, user_profile, helper):
    output_data = []
    items_so_far = []

    for i in range(0, helper.max_length):

        item, score = pick_best(user_recs_df, user_profile, items_so_far, helper)

        items_so_far.append(item)
        output_data.append((userid, item, score))
        new_user_recs = user_recs_df[user_recs_df['itemid']!=item]
        user_recs_df = new_user_recs

    return pd.DataFrame(output_data, columns=['userid', 'itemid', 'score'])

def execute(recoms_df, train_df, helper):
    result = []

    for userid in list(set(recoms_df['userid'])):
#        print('list reranked for user #',userid)
        result.append(rerank(userid, recoms_df[recoms_df['userid']==userid].copy(),
                             train_df[train_df['userid']==userid],
                             helper))

    rr_df = pd.concat(result)
    return rr_df


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


RESULT_FILE_PATTERN = 'out-\d+.txt'
INPUT_FILE_PATTERN = 'cv_\d+'

def enumerate_results(result_path):
    files = os.listdir(result_path)
    pat = re.compile(RESULT_FILE_PATTERN)
    return [file for file in files if pat.match(file)]

if __name__ == '__main__':
    args = read_args()
    #print(args)
    config = read_config_file(args['conf'], args['target'])
    result_files = enumerate_results(args['original'])

    split_path = config.get_files().get_split_path()
    # split_names = os.listdir(split_path)

    data_dir = config.get_prop_dict()['dfs.data.dir']
    item_feature_file = config.get_prop_dict()['data.itemfeature.path']
    protected = config.get_prop_dict()['data.protected.feature']

    item_feature_path = Path(data_dir) / item_feature_file

    item_feature_df = None

    if not item_feature_path.exists():
        print("Cannot locate item features. Path: " + item_feature_path)
        exit(-1)
    else:
        item_feature_df = pd.read_csv(item_feature_path, names=['itemid', 'feature', 'value'])
        item_feature_df.set_index('itemid', inplace=True)

    helper = FarHelper()
    helper.protected_set = get_protected_set(item_feature_df)
    helper.lam = float(args['lambda'])
    helper.max_length = int(args['max_len'])
    helper.binary = args['binary']=='True'

    for file_name in result_files:

        # reading the result
        input_file_path = Path(args['original'] + '/' + file_name)

        # reading the training set
        cv_path = str(split_path) + '/cv_' + re.findall('\d+', file_name)[0] + '/train.txt'
        tr_file_path = Path(cv_path)

        tr_df = None
        if tr_file_path.exists():
            tr_df = pd.read_csv(tr_file_path, names=['userid', 'itemid', 'score'], sep='\t')
        else:
            print('Cannot locate training data: ' + tr_file_path)
            exit(-1)

        if input_file_path.exists():
            recoms_df = pd.read_csv(input_file_path, names=['userid', 'itemid', 'score'])

            reranked_df = execute(recoms_df, tr_df, helper)

            output_file_path = Path(args['result'] + '/' + file_name)
            print('Reranking for ', output_file_path)
            reranked_df.to_csv(output_file_path, header=None, index=False)
