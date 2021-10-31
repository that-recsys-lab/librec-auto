#Name: Zijun Liu
#File: Deep Learning Recommendation Algorithm
#CLKM 2021
from librec_auto.core import read_config_file
import os
import re
import numpy as np
from pathlib import Path
import argparse
import sys
import os
import torch
import cornac
import papermill as pm
# import scrapbook as sb
import pandas as pd

from librec_auto.recommenders.reco_utils.evaluation.python_evaluation import map_at_k, ndcg_at_k, precision_at_k, recall_at_k
from librec_auto.recommenders.reco_utils.recommender.cornac.cornac_utils import predict_ranking
from librec_auto.recommenders.reco_utils.common.timer import Timer
from librec_auto.recommenders.reco_utils.common.constants import SEED

RESULT_FILE_PATTERN = 'out-\d+.txt'

def read_args():
    parser = argparse.ArgumentParser(description='nnRec')
    #parser.add_argument('conf', help='Name of configuration file')
    #parser.add_argument('split_directory', help='Path to original results directory')
    #parser.add_argument('result', help='Path to destination results directory')
    parser.add_argument('--model', choices=['BiVAE'],
                        default='BiVAE')
    parser.add_argument('--TOP_K', type=int, default=10)
    parser.add_argument('--LATENT_DIM', type=int, default=50)
    parser.add_argument('--ENCODER_DIMS', type=int, default=100)
    parser.add_argument('--ACT_FUNC', type=str, default="tanh")
    parser.add_argument('--LIKELIHOOD', type=str, default="pois")
    parser.add_argument('--NUM_EPOCHS', type=int, default=500)
    parser.add_argument('--BATCH_SIZE', type=int, default=128)
    parser.add_argument('--LEARNING_RATE', type=float, default=0.001)

    parser.add_argument('--train', type=str)
    parser.add_argument('--test', type=str)
    parser.add_argument('--result_file', type=str)

    input_args = parser.parse_args()
    return vars(input_args)

def get_top_k(dataframe, k):
    user_unique_set = set(dataframe['userID'])
    return_dataframe = pd.DataFrame()
    for i in user_unique_set:
        dataframe_by_user = dataframe.loc[dataframe['userID'] == i]
        dataframe_by_user = dataframe_by_user.sort_values(by='prediction', ascending=False)[:k]
        return_dataframe = return_dataframe.append(dataframe_by_user)
    return return_dataframe

def main():
    args = read_args()
    model = args['model']
    top_k = args['TOP_K']
    latent_dim = args['LATENT_DIM']
    encoder_dims = []
    encoder_dims.append(args['ENCODER_DIMS'])
    act_func = args['ACT_FUNC']
    likelihood = args['LIKELIHOOD']
    num_epochs = args['NUM_EPOCHS']
    batch_size = args['BATCH_SIZE']
    learning_rate = args['LEARNING_RATE']

    training_path = args['train']
    test_path = args['test']
    result_file_path = args['result_file']


    if model == 'BiVAE':
        train = pd.read_csv(training_path,
                            sep="	", header=None)
        train.columns = ["userID", "itemID", "rating"]
        test = pd.read_csv(test_path,
                           sep="	", header=None)
        test.columns = ["userID", "itemID", "rating"]

        train_set = cornac.data.Dataset.from_uir(train.itertuples(index=False), seed=SEED)
        print('Number of users: {}'.format(train_set.num_users))
        print('Number of items: {}'.format(train_set.num_items))

        #train model
        bivae = cornac.models.BiVAECF(
            k=latent_dim,
            encoder_structure=encoder_dims,
            act_fn=act_func,
            likelihood=likelihood,
            n_epochs=num_epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            seed=SEED,
            use_gpu=torch.cuda.is_available(),
            verbose=True
        )
        with Timer() as t:
            bivae.fit(train_set)
        print("Took {} seconds for training.".format(t))

        with Timer() as t:
            all_predictions = predict_ranking(bivae, train, usercol='userID', itemcol='itemID', remove_seen=True)
            final_result = get_top_k(all_predictions, top_k)
            final_result.to_csv(result_file_path, header=None, index=None, sep=' ')
        print("Took {} seconds for prediction.".format(t))

if __name__ == '__main__':
    main()

