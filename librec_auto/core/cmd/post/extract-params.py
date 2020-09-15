'''
Author: Zijun Liu
Description:
       This script is used to extract the experimental parameters and store it into csv
'''
import argparse
from librec_auto import read_config_file
from librec_auto.util import Status
from librec_auto.util import log_file
import webbrowser

import matplotlib
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

extract_params_format = "extract_{}_params"

def get_metric_info(files):
    metric_info = {}
    for sub_paths in files.get_sub_paths_iterator():
        status = Status(sub_paths)
        if status.is_completed():
            params = status.m_params
            vals = status.m_vals
            log = status.m_log
            metric_info[status.m_name] = (params, vals, log)
    return metric_info

def extract_whole_info(config):
    files = config.get_files()
    metric_info = get_metric_info(config.get_files())
    exp_name = []
    for key in metric_info:
        exp_name.append(key)
    factor = []
    number_factor = []
    Recall_list = []
    Precision_list = []
    ndcg_list = []
    for value in metric_info.values():
        factor.extend(value[0])
        number_factor.extend(value[1])
        Recall_list.extend(value[2].get_metric_values("Recall"))
        Precision_list.extend(value[2].get_metric_values("Precision"))
        ndcg_list.extend(value[2].get_metric_values("NormalizedDCG"))
    split_no = []
    for i in range(0, int(len(Recall_list)/2)):
        split_no.append(i+1)
    split_no.pop()
    split_no.append(-1)
    split_no = split_no*len(exp_name)
    number_factor = np.repeat(number_factor, int(len(Recall_list)/2))
    exp_name = np.repeat(exp_name, int(len(Recall_list)/2))
    param_file = pd.DataFrame(columns=("Experiment", "split no", "rec.factor.number", "Recall", "Precision", "NormalizedDCG"))
    param_file = param_file.append(
        pd.DataFrame({"Experiment": exp_name,
                      "split no": split_no,
                      "rec.factor.number": number_factor,
                      "Recall": Recall_list,
                      "Precision": Precision_list,
                      "NormalizedDCG": ndcg_list}))
    return param_file

def extract_average_info(config):
    files = config.get_files()
    metric_info = get_metric_info(config.get_files())
    exp_name = []
    for key in metric_info:
        exp_name.append(key)
    factor = []
    number_factor = []
    Recall_list = []
    Precision_list = []
    ndcg_list = []
    for value in metric_info.values():
        factor.extend(value[0])
        number_factor.extend(value[1])
        Recall_list.extend([[value[2].get_metric_values("Recall")][-1]])
        Precision_list.extend([[value[2].get_metric_values("Precision")][-1]])
        ndcg_list.extend([[value[2].get_metric_values("NormalizedDCG")][-1]])
    split_no = []
    for i in range(0, int(len(exp_name))):
        split_no.append(-1)
    param_file = pd.DataFrame(
        columns=("Experiment", "split no", "rec.factor.number", "Recall", "Precision", "NormalizedDCG"))
    param_file = param_file.append(
        pd.DataFrame({"Experiment": exp_name,
                      "split no": split_no,
                      "rec.factor.number": number_factor,
                      "Recall": Recall_list,
                      "Precision": Precision_list,
                      "NormalizedDCG": ndcg_list}))
    return param_file

def generate_experimental_parameters_csv(dframe, repo, choice):
    dframe.to_csv(repo+extract_params_format.format(choice))
    print ("Done creating csv file to store {} experimental parameters".format(choice))

def read_args():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(description="Extract the experimental parameters")
    parser.add_argument('conf', help='Path to configuration file')
    parser.add_argument('target', help='Experiment target')
    parser.add_argument('--choice', help='Type of csv', choices=['No', 'average', 'whole', 'both'])
    parser.add_argument('--repository', help="export the csv repository")
    input_args = parser.parse_args()
    return vars(input_args)

if __name__ == '__main__':
    args = read_args()
    config = read_config_file(args['conf'], args['target'])

    choice = args['choice']
    repo = args['repository']

    if choice == "No":
        exit()
    elif choice == "average":
        avg = extract_average_info(config)
        generate_experimental_parameters_csv(avg, repo, choice)
    elif choice == "whole":
        woe = extract_whole_info(config)
        generate_experimental_parameters_csv(woe, repo, choice)
    elif choice == "both":
        avg = extract_average_info(config)
        woe = extract_whole_info(config)
        generate_experimental_parameters_csv(woe, repo, 'whole')
        generate_experimental_parameters_csv(avg, repo, 'average')
    else:
        print ('Please input correct type name in XML file')