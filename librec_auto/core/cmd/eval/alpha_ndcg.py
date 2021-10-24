import argparse
import numpy as np
from math import log

import csv

from librec_auto.core.eval import ListBasedMetric
from librec_auto.core import read_config_file, ConfigCmd

class AlphaNdcgMetric(ListBasedMetric):
    def __init__(self, file_name,alpha=0.5):
        #query_topics, doc_topics,
        self._name = 'AlphaNDCG'
        self.alpha = alpha
        self.file_name = file_name
        self.matrix = self.load_csv(file_name)
        #self.query_topics=query_topics
        #self.doc_topics=doc_topics

    # Rating 1st column: 6040  -  user id
    # Rating 2nd column: 3946  -  item id
    def load_csv(self,file_name):
        # col_name: user 6040
        # row_name: item 3946
        users = 0
        items = 0
        fp = open(file_name)

        for line in fp:
            tokens = line.strip().split(",")
            user_id = int(tokens[0])
            item_id = int(tokens[1])
            if user_id > users:
                users = user_id
            if item_id > items:
                items = item_id
        fp.close()

        matrix = [[0 for i in range(items)] for j in range(users)]  # column,row

        fp = open(file_name)
        for line in fp:
            tokens = line.strip().split(",")
            user_id = int(tokens[0]) - 1
            item_id = int(tokens[1]) - 1
            rating = int(tokens[2])
            matrix[user_id][item_id] = rating
        fp.close()

        return np.array(matrix)

    #

    '''def load_query_topics(self,query_topics):
        self.query_topic_dict=query_topics



    def load_doc_topics(self,doc_topics):
        self.doc_topics_dict=doc_topics
'''

    def process_kth_row(self,row_k):
        matrix = self.matrix
        matrix = np.array(matrix)
        result=0
        for i in range(len(matrix)):
            if matrix[row_k][i] != 0:
                non_zero = (matrix[0:row_k, i] != 0).sum()
                result += self.alpha ** non_zero
        return result
    #G
    # sum of i from 1 to m
    # 1st column - user: 1-7
    # 2nd column - item: 1-7
    # 3rd column - score:1-5
    def gain_val(self):
        '''
        d_k = horizontal
        i = vertical
        G[0] = 3
        G[1] = (0.5) ^ 1+(0.5) ^ 0+(0.5) ^ 0
        G[2] = (0.5) ^ 0+(0.5) ^ 0
        G[3] = (0.5) ^ 1+(0.5) ^ 0+(0.5) ^ 2+(0.5) ^ 0
        ...
        '''
        matrix = self.matrix
        matrix = np.array(matrix)

        G = [(matrix[0] != 0).sum()]

        for i in range(1,len(matrix)):
            G.append(self.process_kth_row(i))
        return G


    def cumulative_gain_val(self, G):
        # CG
        '''
        CG[1] = G[1]
        CG[2] = G[1]+G[2]
        CG[3] = G[1]+G[2]+G[3]
        '''

        G = np.array(G)
        result_cg = [G[0]]
        for i in range(1,len(G)):
            result_cg.append(G[0:i+1].sum())
        return result_cg

    # DCG
    def discount_cumulative_gain_val(self,G):

        G = np.array(G)
        result_dcg = []
        for i in range(0,len(G)):
            top = G[0:i+1]
            bottom = np.log2(np.arange(2,i+3))
            result_dcg.append((top/bottom).sum())

        return result_dcg

    '''
    DCG[1] = G[1] / LOG[1+1]
    DCG[2] = G[1] / LOG[1+1] + G[2] / LOG[1+2]
    DCG[3] = G[1] / LOG[1+1] + G[2] / LOG[1+2] +G[3] / LOG[1+3]
    '''





    # ideal G'
    def ideal_gain_val(self,G):
        G = np.array(G)
        ideal_G = np.sort(G)[::-1]
        return ideal_G




    # ideal CG'
    def ideal_cumulative_gain_val(self, ideal_G):
        ideal_G = np.array(ideal_G)
        ideal_result_dcg = [ideal_G[0]]
        for i in range(1, len(ideal_G)):
            ideal_result_dcg.append(ideal_G[0:i + 1].sum())

        return ideal_result_dcg


    # ideal DCG'
    def ideal_discount_cumulative_gain_val(self,ideal_G):

        ideal_G = np.array(ideal_G)
        ideal_result_dcg = []
        for i in range(0,len(ideal_G)):
            top = ideal_G[0:i+1]
            bottom = np.log2(np.arange(2,i+3))
            ideal_result_dcg.append((top/bottom).sum())

        return ideal_result_dcg


    def result_ndcg(self,G,ideal_G):
        result_dcg = model.discount_cumulative_gain_val(G)
        result_ideal_dcg = model.ideal_discount_cumulative_gain_val(ideal_G)

        ndcg = []
        for i in range(len(result_dcg)):
            ndcg.append(result_dcg[i]/result_ideal_dcg[i])

        return ndcg







if __name__ == '__main__':

    model = AlphaNdcgMetric(file_name="/Users/weiyao/Desktop/testing.csv", alpha=0) #，alpha=0.5

    #matrix_prac=model.load_csv("/Users/weiyao/Desktop/testing.csv")
    #print(matrix_prac)

    print("Matrix: ")
    print(model.matrix)
    print()

    print("G, CG, DCG:")
    G = model.gain_val()
    print(G)
    result_cg = model.cumulative_gain_val(G)
    print(result_cg)
    result_dcg = model.discount_cumulative_gain_val(G)
    print(result_dcg)
    print()
    print("G', CG', DCG':")
    
    #ideal 
    ideal_G = model.ideal_gain_val(G)
    print(ideal_G)
    ideal_result_cg = model.ideal_cumulative_gain_val(ideal_G)
    print(ideal_result_cg)
    ideal_result_dcg = model.ideal_discount_cumulative_gain_val(ideal_G)
    print(ideal_result_dcg)

    print()

    print("ndcg: ")
    ndcg_list = model.result_ndcg(G,ideal_G)
    print(ndcg_list)
    print()
    print("ndcg value: ")
    ndcg = np.average(ndcg_list)
    print(ndcg)