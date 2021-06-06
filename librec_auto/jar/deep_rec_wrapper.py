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
warnings.filterwarnings('ignore')

def read_args():
    parser = argparse.ArgumentParser(description='nnRec')
    parser.add_argument('--model', choices=['MF', 'NNMF', 'NRR', 'I-AutoRec', 'U-AutoRec',
                                            'FM', 'NFM', 'AFM', 'DEEP-FM'],
                        default='DEEP-FM')
    parser.add_argument('--epochs', type=int, default=200)
    parser.add_argument('--batch_size', type=int, default=256)  # 128 for unlimpair
    parser.add_argument('--learning_rate', type=float, default=1e-3)  # 1e-4 for unlimpair
    parser.add_argument('--reg_rate', type=float, default=0.1)  # 0.01 for unlimpair
    parser.add_argument('--num_factors', type=int, default=10)
    parser.add_argument('--display_step', type=int, default=1000)
    parser.add_argument('--show_time', type=bool, default=False)
    parser.add_argument('--T', type=int, default=2)
    parser.add_argument('--deep_layers', type=str, default="200, 200, 200")
    parser.add_argument('--field_size', type=int, default=10)

    input_args = parser.parse_args()
    return vars(input_args)

def main():
    args = read_args()
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
        'epochs': epoch_var,
        'batch_size': batch_size_var,
        'learning_rate': learning_rate_var,
        'reg_rate': reg_rate_var,
        'num_factors': num_factors_var,
        'display_step': display_step_var,
        'show_time': show_time_var[0],
        'T': t_var,
        'layers': list(map(int, deep_layers_var.split(','))),
        'field_size': field_size_var
    }


if __name__ == '__main__':
    main()

