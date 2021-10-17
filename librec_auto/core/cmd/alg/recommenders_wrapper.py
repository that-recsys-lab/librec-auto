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
#import papermill as pm
# import scrapbook as sb
import pandas as pd

#from recommenders.reco_utils.evaluation.python_evaluation import map_at_k, ndcg_at_k, precision_at_k, recall_at_k
#from recommenders.models.cornac.cornac_utils import predict_ranking
#from recommenders.reco_utils.common.timer import Timer
from recommenders.utils.constants import SEED
from recommenders.models.vae.standard_vae import StandardVAE

def read_args():
    parser = argparse.ArgumentParser(description='nnRec')
    #parser.add_argument('conf', help='Name of configuration file')
    #parser.add_argument('split_directory', help='Path to original results directory')
    #parser.add_argument('result', help='Path to destination results directory')
    '''
    # top k items to recommend
    TOP_K = 10

    # Model parameters
    LATENT_DIM = 50
    ENCODER_DIMS = [100]
    ACT_FUNC = "tanh"
    LIKELIHOOD = "pois"
    NUM_EPOCHS = 500
    BATCH_SIZE = 128
    LEARNING_RATE = 0.001
    '''
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

    input_args = parser.parse_args()
    return vars(input_args)

def main():
    args = read_args()
    #config_var = args['config']
    #split_directory_var = args['split_directory']
    #result_var = args['result']
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

    if model == 'BiVAE':
        train = pd.read_csv('/Users/liuzijun1/Desktop/librec-auto/librec-auto-demo2020/data/split/cv_1/train.txt',
                            sep="	", header=None)
        train.columns = ["userID", "itemID", "rating"]
        test = pd.read_csv('/Users/liuzijun1/Desktop/librec-auto/librec-auto-demo2020/data/split/cv_1/test.txt',
                           sep="	", header=None)
        test.columns = ["userID", "itemID", "rating"]

        train_set = cornac.data.Dataset.from_uir(train.itertuples(index=False), seed=SEED)
        print('Number of users: {}'.format(train_set.num_users))
        print('Number of items: {}'.format(train_set.num_items))

        #train model
        bivae = StandardVAE(
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

        StandardVAE(n_users=train_set.num_users,  # Number of unique users in the training set
                    original_dim=train_data.shape[1],  # Number of unique items in the training set
                    intermediate_dim=INTERMEDIATE_DIM,
                    latent_dim=latent_dim,
                    n_epochs=num_epochs,
                    batch_size=batch_size,
                    k=TOP_K,
                    verbose=0,
                    seed=SEED,
                    save_path=WEIGHTS_PATH,
                    drop_encoder=0.5,
                    drop_decoder=0.5,
                    annealing=False,
                    beta=1.0
                    )
        with Timer() as t:
            bivae.fit(train_set)
        print("Took {} seconds for training.".format(t))

        with Timer() as t:
            all_predictions = predict_ranking(bivae, train, usercol='userID', itemcol='itemID', remove_seen=True)
            np.savetxt('/Users/liuzijun1/Desktop/librec-auto/librec-auto-demo2020/demo02/exp00000/result/result.txt', all_predictions.values, fmt='%d')
        print("Took {} seconds for prediction.".format(t))

if __name__ == '__main__':
    main()

