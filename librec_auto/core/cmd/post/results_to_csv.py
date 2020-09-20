'''
Author: Zijun Liu
Description:
       This script is used to extract the experimental parameters and store it into csv
'''
import argparse
from librec_auto.core import read_config_file
from librec_auto.core.util import Status
from collections import defaultdict

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

def extract_full_info(config):
    metric_info = get_metric_info(config.get_files())
    exp_frames = []
    table_values = defaultdict(list)
    time_stamp = None

    for exp in metric_info.keys():
        params, vals, log = metric_info[exp]
        time_stamp = log.get_time_stamp()
        entry_count = log.get_kcv_count()
        table_values['Experiment'] = np.repeat(exp, entry_count)
        table_values['Split'] = range(0, entry_count)

        for (param, val) in zip(params, vals):
            table_values[param] = np.repeat(val, entry_count)

        for metric in log.get_metrics():
            table_values[metric] = log.get_metric_values(metric)[0:entry_count]

        exp_df = pd.DataFrame(table_values)
        exp_frames.append(exp_df)

    exp_results = pd.concat(exp_frames, axis=0, ignore_index=True)
    return (exp_results, time_stamp)


def extract_summary_info(config):
    metric_info = get_metric_info(config.get_files())
    table_values = defaultdict(list)
    time_stamp = None

    for exp in metric_info.keys():
        params, vals, log = metric_info[exp]
        time_stamp = log.get_time_stamp()
        table_values['Experiment'].append(exp)

        for (param, val) in zip(params, vals):
            table_values[param].append(val)

        for metric in log.get_metrics():
            table_values[metric].append(log.get_metric_values(metric)[-1])

    exp_results = pd.DataFrame(table_values)
    return (exp_results, time_stamp)


def save_data(df, choice, time_stamp):
    save_path = config.get_files().get_post_path() / f'study-results-{choice}_{time_stamp}.csv'
    df.to_csv(save_path, index=False)

def read_args():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(description="Extract the experimental parameters")
    parser.add_argument('conf', help='Path to configuration file')
    parser.add_argument('target', help='Experiment target')
    parser.add_argument('--option', help='Type of csv', choices=['summary', 'full', 'all'])
    input_args = parser.parse_args()
    return vars(input_args)

if __name__ == '__main__':
    args = read_args()
    config = read_config_file(args['conf'], args['target'])

    choice = args['option']

    if choice == "summary":
        df, time_stamp = extract_summary_info(config)
        save_data(df, choice, time_stamp)
    elif choice == "full":
        df, time_stamp = extract_full_info(config)
        save_data(df, choice, time_stamp)
    elif choice == "all":
        df, time_stamp = extract_summary_info(config)
        save_data(df, "summary", time_stamp)
        df, time_stamp = extract_full_info(config)
        save_data(df, "full", time_stamp)

    else:
        print ('Unrecognized option for results_to_csv')
