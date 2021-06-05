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
    print("Model is {}".format(model_var))

if __name__ == '__main__':
    main()

