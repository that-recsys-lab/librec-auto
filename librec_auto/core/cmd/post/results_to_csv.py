'''
Author: Zijun Liu
Description:
       This script is used to extract the experimental parameters and store it into csv
'''
import argparse
from librec_auto.core.util.study_status import StudyStatus
from librec_auto.core import read_config_file
from librec_auto.core.util import Status
from collections import defaultdict
from pathlib import Path

import pandas as pd
import numpy as np

extract_params_format = "extract_{}_params"


def get_metric_info(files):
    metric_info = {}
    for sub_paths in files.get_exp_paths_iterator():
        status = Status(sub_paths)
        if status.is_completed():
            params = status._params
            vals = status._vals
            log = status._log
            metric_info[status._name] = (params, vals, log)
    return metric_info


def extract_full_info(study):
    exp_frames = []
    table_values = defaultdict(list)
    time_stamp = study._timestamp

    # iterate over experiments in study for metric info
    for exp in study._experiments.keys():
        
        curr_exp = study._experiments[exp]
        exp_count = curr_exp._kcv_count
        # each experiment has a _kcv_count attribute, used twice here
        table_values['Experiment'] = np.repeat(curr_exp._name, exp_count)
        table_values['Split'] = range(0, exp_count)

        for (param, val) in study.get_exp_param_values(exp):
            table_values[param] = np.repeat(val, exp_count)
        
        for metric in study.get_metric_names():
            table_values[metric] = curr_exp._metric_info[metric]
        
        exp_df = pd.DataFrame(table_values)
        exp_frames.append(exp_df)
    
    exp_results = pd.concat(exp_frames, axis=0, ignore_index=True)
    print(exp_results)
    return (exp_results, time_stamp)


def extract_summary_info(study):
    table_values = defaultdict(list)
    time_stamp = study._timestamp

    for exp in study._experiments.keys():
        curr_exp = study._experiments[exp]
        table_values['Experiment'].append(curr_exp._name)
        for (param, val) in study.get_exp_param_values(exp):
            table_values[param].append(val)

        for metric in study.get_metric_names():
            table_values[metric].append(curr_exp._metric_avg[metric])

    exp_results = pd.DataFrame(table_values)
    print(exp_results)
    return (exp_results, time_stamp)

def metric_values_float(log, metric):
    str_values = log.get_metric_values(metric)['cv_results']
    return [float(val) for val in str_values]


def save_data(df, choice, time_stamp):
    save_path = Path('post') / f'study-results-{choice}_{time_stamp}.csv'
    df.to_csv(save_path, index=False)


def read_args():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(
        description="Extract the experimental parameters")
    parser.add_argument('conf', help='Path to configuration file')
    parser.add_argument('--option',
                        help='Type of csv',
                        choices=['summary', 'full', 'all'])
    input_args = parser.parse_args()
    return vars(input_args)


if __name__ == '__main__':
    args = read_args()
    config = read_config_file(args['conf'], ".")
    study = StudyStatus(config)
    choice = args['option']

    if choice == "summary":
        df, time_stamp = extract_summary_info(study)
        save_data(df, choice, time_stamp)
    elif choice == "full":
        df, time_stamp = extract_full_info(study)
        save_data(df, choice, time_stamp)
    elif choice == "all":
        df, time_stamp = extract_summary_info(study)
        save_data(df, "summary", time_stamp)
        df, time_stamp = extract_full_info(study)
        save_data(df, "full", time_stamp)

    else:
        print('Unrecognized option for results_to_csv')
