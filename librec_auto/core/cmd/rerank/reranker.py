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
        self.weight = None

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
        return set((self.item_feature_df[(self.item_feature_df['feature'] == self.protected)
                                       & (self.item_feature_df ['value'] == 1)].index).tolist())

    def similarity(self, feature1, feature2, binary):
        if binary:
            return np.count_nonzero(np.logical_and(feature1, feature2)) / \
                   np.count_nonzero(np.logical_or(feature1, feature2))

        return 1 - distance.cosine(feature1, feature2)


    def update_sim_matrix_dic(self, index1, index2, binary):

        if index1 in self.sim_matrix_dic:
            if index2 in self.sim_matrix_dic[index1]:
                return self.sim_matrix_dic[index1][index2]

        vec_proj1 = self.item_feature_df.loc[[index1, ]]
        vec_proj2 = self.item_feature_df.loc[[index2, ]]

        joined = pd.concat([vec_proj1, vec_proj2], axis=0)
        
        if self.weight is not None:
            for label in self.weight.keys():
                joined.loc[(joined.feature == label), 'value'] *= self.weight[label]

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
        self.total_score = 0
        # self.tol = None
        # self.distribution = None
        # self.rec_dist = 0

    def set_user_helper(self, user_id, rating_df, user_profile, rerank_helper):
        user_helper = User_Helper()
        self.id = user_id

        # user_rating = rating_df.loc[rating_df["userid"] == user_id, [
        #     "rating"]].to_numpy().transpose()[0]

        user_rating = rating_df.loc[rating_df["userid"] == user_id, ["rating"]].to_numpy()

        scaler = MinMaxScaler()

        self.scaled_rating = scaler.fit_transform(user_rating).flatten()
        # self.scaled_rating = user_rating

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

        scaler = MinMaxScaler()

        for k in range(num_item):
            # scoring function
            scores, self.rerank_helper, self.user_helper = self.scoring_function(rec, self.rerank_helper,
                                                                                 self.user_helper)

            max_idx = np.argmax(np.array(scores))
            all_scores[k] = scores[max_idx]

            self.user_helper.item_so_far.append(self.user_helper.item_list[max_idx])
            self.user_helper.item_list = np.delete(self.user_helper.item_list, max_idx)

            self.user_helper.total_score += rec[max_idx]
            rec = np.delete(rec, max_idx)

        # self.user_helper.item_so_far_score = list(all_scores)
        # print(scaler.fit_transform(all_scores))
        # self.user_helper.item_so_far_score = list(scaler.fit_transform(all_scores.reshape(-1, 1)))
        self.user_helper.item_so_far_score = list(scaler.fit_transform(all_scores.reshape(-1, 1)).flatten())
