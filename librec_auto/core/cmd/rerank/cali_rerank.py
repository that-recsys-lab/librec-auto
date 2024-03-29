from librec_auto.core.cmd.rerank import Rerank_Helper, User_Helper, Reranker

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
import math
import warnings

warnings.filterwarnings('ignore')
import multiprocessing


# names=['itemid', 'feature', 'value'])
class FAIRREC(Reranker):
    def FairRec(self,U,P,k,V,alpha,m,n):
    # k size of rec list
    # a is parameter
    # U is set of users - set of userids(column1)
    # P is set of products - set of itemids(column2) (for now)
    # V --> User rating item triples (col1,col3,col2)

    # data --> rating for every item
    # we don't have rating for every item
    # fake the ratings?

    # what is the connection between items such that you can have a producer with multiple items?
    # Have user,item,predictedd,rating for some set of items
    # want user 50 and item 67, return -inf as rating or -1 if rating are all positive
    # want to do it more programatically than that

    # what I could do is basically make a set or dictionary --> users items and ratings, you look it up, when hitting empty spot just return -1

    # the notion of fairness is minimum amount of exposure for items for each producers
        # k is less than producers
        #  EF1 = envy freeness up to 1 product
            # envy free allocation
                # prizes to 10 people
                # no one wants to change, it's envy free
            # each producer should have their product appear once

    # order looking at customers matters

    # Allocation set for each customer, initially it is set to empty set
        print(U)
        print(P)
        print(k)
        print(m)
        print(n)
        print(V[:5])


        A={}
        for u in U:
            A[u]=[]

        # feasible set for each customer, initially it is set to P
        F={}
        for u in U:
            F[u]=P[:]
        #print(sum([len(F[u]) for u in U]))
    
        # number of copies of each producer
        l=int(alpha*m*k/(n+0.0))

        # R= number of rounds of allocation to be done in first GRR
        R=int(math.ceil((l*n)/(m+0.0)))  

        
        # total number of copies to be allocated
        T= l*n
        
        # first greedy round-robin allocation
        [B,F1]=greedy_round_robin(m,n,R,l,T,V,U[:],F.copy())
        F={}
        F=F1.copy()
        # adding the allocation
        for u in U:        
            A[u]=A[u][:]+B[u][:]
        
        # second phase
        u_less=[] # customers allocated with <k products till now
        for u in A:
            if len(A[u])<k:
                u_less.append(u)

        # allocating every customer till k products
        for u in u_less:
            scores=V[u,:] # instead of being matrix, function call either checks, or returns -1
            new=scores.argsort()[-(k+k):][::-1] # go through users
            for p in new:
                if p not in A[u]:
                    A[u].append(p)
                if len(A[u])==k:
                    break

        return A;



    def greedy_round_robin(self, m,n,R,l,T,V,U,F): 
            # greedy round robin allocation based on a specific ordering of customers (assuming the ordering is done in the relevance scoring matrix before passing it here)
            
            # assuming there is no producer with more than 1 item, treats P the same as a set of items

            # creating empty allocations
            B={}
            for u in U:
                B[u]=[]
            
            # available number of copies of each producer
            Z={} # total availability
            P=range(n) # set of producers
            for p in P:
                Z[p]=l
            
            # allocating the producers to customers
            for t in range(1,2): # end of range = R+1
                for i in range(m):
                    if T==0:
                        return B,F
                    u=U[i]
                    # choosing the p_ which is available and also in feasible set for the user
                    possible=[(Z[p]>0)*(p in F[u])*V[u,p] for p in range(n)] 
                    p_=np.argmax(possible) 
                    
                    if (Z[p_]>0) and (p_ in F[u]) and len(F[u])>0:
                        B[u].append(p_)
                        F[u] = list(F[u])
                        F[u].remove(p_)
                        Z[p_]=Z[p_]-1
                        T=T-1
                    else:
                        return B,F
            # returning the allocation
            return B,F;


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
    # parser.add_argument('--lambda', help='The weight for re-ranking. Higher lambda = more diversity.')
    parser.add_argument('--alpha', help='alpha.')
    parser.add_argument('--protected_feature', help='protected feature')

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

#def execute(rerank_helper, item_helper, scoring_function, profile_flag, pat, file_path, split_path, dest_results_path):
def execute(rerank_helper, pat, file_path, split_path, dest_results_path, k, V, alpha):
    tr_df = None

    # k size of rec list
    # a is parameter
    # U is set of users - set of userids(column1)
    # P is set of products - set of itemids(column2) (for now)
    # V --> User rating item triples (col1,col3,col2)

    # FairRec(self,U,P,k,V,alpha,m,n):

    m = re.match(pat, file_path.name)
    cv_count = m.group(1)
    tr_df = load_training(split_path, cv_count)
    if tr_df is None:
        print("no traning data")
        exit(-1)

    rating_df = pd.read_csv(file_path, names=['userid', 'itemid', 'rating'])
    # far_rerank call needs to be replaced with Fairec - turn into a class?
    arg_1 = range(len(rating_df))
    arg_2 = range(max(rating_df['itemid'].values.tolist()))
    m = len(rating_df)
    n = max(rating_df['itemid'].values.tolist())

    #may need to swap n and m
    arr =[[-1 for i in range(len(m))] for j in range(len(n))]

    with open(file_path, 'r') as f:
        for line in f:
            split = line.split()
            arr[int(split[1])][int(split[0])] = int(split[2])

    

    re_ranker = FairRec(arg_1, arg_2, k, arr, V, alpha, m, n)

    reranked_df, rerank_helper = re_ranker.reranker()
    output_reranked(reranked_df, dest_results_path, file_path)


def main():
    args = read_args()

    # args = {'conf':'config01.xml',
    # 'original':'/home/kadekool/librec-auto-demo2021/demo01/exp00000/original',
    # 'result':'/home/kadekool/librec-auto-demo2021/demo01/exp00000/result',
    # '--max_len':'2',
    # '--alpha':'0.5',
    # '--protected_feature':'new'}
    # ['/home/kadekool/librec-master/env/bin/python', '/home/kadekool/librec-master/env/lib/python3.8/site-packages/librec_auto-0.2.13-py3.8.egg/librec_auto/core/cmd/rerank/cali_rerank.py', 'config01.xml', '/home/kadekool/librec-auto-demo2021/demo01/exp00000/original', '/home/kadekool/librec-auto-demo2021/demo01/exp00000/result', '--max_len=10', '--alpha=0.5', '--protected_feature=new']

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

    #item_helper = set_item_helper(item_feature_df)

    #rerank_helper = set_rerank_helper(args, config, item_helper)
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
