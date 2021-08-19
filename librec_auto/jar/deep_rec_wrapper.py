#Name: Zijun Liu
#File: Deep Learning Recommendation Algorithm
#CLKM 2021


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
import tensorflow as tf
from scipy.sparse import csc_matrix, csr_matrix

from DeepRec.models.rating_prediction.deepfm import DeepFM
from DeepRec.utils.load_data.load_data_content import load_data_fm

warnings.filterwarnings('ignore')

def read_args():
    parser = argparse.ArgumentParser(description='nnRec')
    #parser.add_argument('conf', help='Name of configuration file')
    #parser.add_argument('split_directory', help='Path to original results directory')
    #parser.add_argument('result', help='Path to destination results directory')
    parser.add_argument('--model', choices=['MF', 'NNMF', 'NRR', 'I-AutoRec', 'U-AutoRec',
                                            'FM', 'NFM', 'AFM', 'DEEP-FM'],
                        default='DEEP-FM')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch_size', type=int, default=256)  # 128 for unlimpair
    parser.add_argument('--learning_rate', type=float, default=1e-3)  # 1e-4 for unlimpair
    parser.add_argument('--reg_rate', type=float, default=0.1)  # 0.01 for unlimpair
    parser.add_argument('--num_factors', type=int, default=10)
    parser.add_argument('--display_step', type=int)
    parser.add_argument('--show_time', type=bool, default=False)
    parser.add_argument('--T', type=int, default=2)
    parser.add_argument('--deep_layers', type=str, default="200, 200, 200")
    parser.add_argument('--field_size', type=int, default=10)

    input_args = parser.parse_args()
    return vars(input_args)

def load_data(path='/Users/liuzijun1/Desktop/librec-auto/librec-auto-demo2020/data/split', header=['user_id', 'item_id', 'rating']):
    files = os.listdir(path)
    num_files = len(files) - 1
    data = []

    for i in range(num_files):
        path_cv = path + "/" + files[i + 1]
        path_train = path_cv + "/" + "train.txt"
        path_test = path_cv + "/" + "test.txt"

        df_train = pd.read_csv(path_train, names=header, sep='\t')
        df_test = pd.read_csv(path_test, names=header, sep='\t')

        # n_users = df_train.user_id.unique().shape[0]
        # n_items = df_train.item_id.unique().shape[0]

        df = pd.concat([df_train, df_test])

        users = df.user_id.unique()
        items = df.item_id.unique()
        n_users = users.shape[0]
        n_items = items.shape[0]

        user_dict = {}
        item_dict = {}

        for i in range(n_users):
            user_dict[users[i]] = i

        for i in range(n_items):
            item_dict[items[i]] = i

        train_data = df_train
        test_data = df_test

        train_row = []
        train_col = []
        train_rating = []

        for line in train_data.itertuples():
            u = user_dict[line[1]]
            i = item_dict[line[2]]
            train_row.append(u)
            train_col.append(i)
            train_rating.append(line[3])
        train_matrix = csr_matrix((train_rating, (train_row, train_col)), shape=(n_users, n_items))

        test_row = []
        test_col = []
        test_rating = []
        for line in test_data.itertuples():
            u = user_dict[line[1]]
            i = item_dict[line[2]]
            # test_row.append(line[1] - 1)
            # test_col.append(line[2] - 1)
            test_row.append(u)
            test_col.append(i)
            test_rating.append(line[3])
        test_matrix = csr_matrix((test_rating, (test_row, test_col)), shape=(n_users, n_items))
        print("Load data finished. Number of users:", n_users, "Number of items:", n_items)
        data.append([train_matrix.todok(), test_matrix.todok(), n_users, n_items])

    return data

def main():
    args = read_args()
    #config_var = args['config']
    #split_directory_var = args['split_directory']
    #result_var = args['result']
    model_var = args['model']
    epoch_var = args['epochs']
    batch_size_var = args['batch_size']
    learning_rate_var = args['learning_rate']
    reg_rate_var = args['reg_rate']
    num_factors_var = args['num_factors']
    display_step_var = args['display_step']
    show_time_var = args['show_time']
    t_var = args['T']
    deep_layers_var = args['deep_layers']
    field_size_var = args['field_size']

    kws = {
        #'config': config_var,
        #'split_directory': split_directory_var,
        #'result': result_var,
        'epochs': epoch_var,
        'batch_size': batch_size_var,
        'learning_rate': learning_rate_var,
        'reg_rate': reg_rate_var,
        'num_factors': num_factors_var,
        'display_step': display_step_var,
        'show_time': show_time_var,
        'T': t_var,
        'layers': list(map(int, deep_layers_var.split(','))),
        'field_size': field_size_var
    }

    data = load_data()

    '''
    for i in range(0, len(data)):
        train_data, test_data, n_user, n_item = data[i]

        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True

        with tf.Session(config=config) as sess:
            model = None
            if model_var == "DEEP-FM":
                train_data, test_data, feature_M = load_data_fm()
                n_user = 957
                n_item = 4082
                model = DeepFM(sess, n_user, n_item, **kws)
                model.build_network(feature_M)

            # build and execute the model
            if model is not None:
                if model_var in ('FM', 'NFM', 'DEEP-FM', 'AFM'):
                    model.execute(train_data, test_data)
                else:
                    model.build_network()
                    model.execute(train_data, test_data)
    '''

if __name__ == '__main__':
    main()

