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
class FAIRREC():
    def __init__(self):
        pass
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
        # print("U",U)
        # print("P",P)
        # print("k",k)
        # print("m",m)
        # print("n",n)
        # print("V", V[:5])

        alpha = float(alpha)
        m = int(m)
        n= int(n)
        k = int(k)


        A={}
        # for u in U:
        #     A[u]=[]
        A = {u:[] for u in U}

        # feasible set for each customer, initially it is set to P
        F={}
        # for u in U:
        #     F[u]=P[:]
        F = {u:P[:] for u in U}

        print("F")
        #print(sum([len(F[u]) for u in U]))
    
        # number of copies of each producer
        l=int(alpha*m*k/(n+0.0))

        # R= number of rounds of allocation to be done in first GRR
        R=int(math.ceil((l*n)/(m+0.0)))  

        
        # total number of copies to be allocated
        T= l*n
        
        print("T")
        # first greedy round-robin allocation
        print("callng G")
        [B,F1]=self.greedy_round_robin(m,n,R,l,T,V,U[:],F.copy())
        print("returning G")
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

        print("u_less")
        # allocating every customer till k products
        for u in u_less:
            scores=V[u,:] # instead of being matrix, function call either checks, or returns -1
            new=scores.argsort()[-(k+k):][::-1] # go through users
            for p in new:
                if p not in A[u]:
                    A[u].append(p)
                if len(A[u])==k:
                    break

        # print("returning A")
        # print(A)
        return A



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
                    print(i, m)
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
            return B,F


    # def __init__(self, rating, training, rerank_helper):
    #     Reranker.__init__(self, rating, training, rerank_helper, self.fun())


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
    # parser.add_argument('--protected_feature', help='protected feature')

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
def execute(pat, file_path, split_path, dest_results_path, k, alpha):
    tr_df = None

    # k size of rec list
    # a is parameter
    # U is set of users - set of userids(column1)
    # P is set of products - set of itemids(column2) (for now)
    # V --> User rating item triples (col1,col3,col2)

    # FairRec(self,U,P,k,V,alpha,m,n):



    # m = re.match(pat, file_path.name)
    # cv_count = m.group(1)
    # tr_df = load_training(split_path, cv_count)
    # if tr_df is None:
    #     print("no training data")
    #     exit(-1)

    # print("reading")
    # print(file_path)
    rating_df = pd.read_csv(file_path, names=['userid', 'itemid', 'rating'])
    
    user_id_list = rating_df['userid'].values.tolist()
    item_id_list = rating_df['itemid'].values.tolist()
    rating_list = rating_df['rating'].values.tolist()

    user_dict = dict(zip(user_id_list, range(len(user_id_list))))
    item_dict = dict(zip(item_id_list, range(len(item_id_list))))

    user_id_list = [int(user_dict[x]) for x in user_id_list]
    item_id_list = [int(item_dict[x]) for x in item_id_list]
    rating_list = [float(x) for x in rating_list]

    # V = [(user_id_list[i], rating_list[i], item_id_list[i]) for i in range(len(rating_df))]

    # arg_1 = range(len(rating_df))
    # arg_2 = range(max(rating_df['itemid'].values.tolist()))

    # print(rating_df)

    m = max(user_id_list)
    n = max(item_id_list)

    # with open(file_path, 'r') as f:
    #     for line in f:
    #         # print(line)
    #         split = line.split(',')
    #         m = max(m, int(split[1]))
    #         n = max(n, int(split[0]))
    m += 1
    n += 1 #check if kiva is one indexed

    arr =[[-1 for i in range(m)] for j in range(n)]

    # print(m,n)

    with open(file_path, 'r') as f:
        for line in f:
            split = line.split(',')
            arr[int(split[1])][int(split[0])] = float(split[2])

    # print("calling Fairrec")

    re_ranker = FAIRREC()
    # FairRec(self,U,P,k,V,alpha,m,n):

    # k size of rec list
    # a is parameter
    # U is set of users - set of userids(column1)
    # P is set of products - set of itemids(column2) (for now)
    # V --> User rating item triples (col1,col3,col2)

    U = range(m)
    P = range(n)
    c = re_ranker.FairRec(U, P, k, np.array(arr), alpha, m, n)

    # reranked_df, rerank_helper = re_ranker.reranker()

    c= list(c.values())

    reranked_array = []

    for i in range(len(c)):
        for j in range(len(c[i])):
            reranked_array.append([i, c[i][j], 1/(j+1)])


    reranked_df = pd.DataFrame(reranked_array)

    output_reranked(reranked_df, dest_results_path, file_path)
    # print(c)
    return c


def main():
    args = read_args()

    config = read_config_file(args['conf'], '.')

    original_results_path = Path(args['original'])
    result_files = [file for file in original_results_path.iterdir()]

    dest_results_path = Path(args['result'])

    data_dir = single_xpath(config.get_xml(), '/librec-auto/data/data-dir').text

    data_path = Path(data_dir)
    data_path = data_path.resolve()

    # item_feature_df = load_item_features(config, data_path)
    # if item_feature_df is None:
    #     exit(-1)

    # item_helper = set_item_helper(item_feature_df)

    #rerank_helper = set_rerank_helper(args, config, item_helper)
    # rerank_helper = Rerank_Helper()
    # rerank_helper.set_rerank_helper(args, config, item_feature_df)

    split_path = data_path / 'split'
    pat = re.compile(RESULT_FILE_PATTERN)

    # method = args['method']

    p = []

    # print(args)

    k = args['max_len']

    alpha = args['alpha']

    # print(pat, result_files, split_path, dest_results_path)

    for file_path in result_files:
        print(file_path)
        p1 = multiprocessing.Process(target=execute, args=(
        pat, file_path, split_path, dest_results_path, k, alpha))
        p.append(p1)
        p1.start()

    for p1 in p:
        p1.join()

    print("done")
if __name__ == '__main__':
    main()
