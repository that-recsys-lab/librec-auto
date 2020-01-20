
import argparse
from pathlib import Path
from librec_auto import read_config_file
from librec_auto import ConfigCmd
from librec_auto.util import LogFile, Status
from librec_auto.util import SubPaths
#import librec_auto.utils.util
import sys

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')  # For non-windowed plotting

viz_file_pattern_bar = "viz-bar-{}.pdf"
viz_file_pattern_box = "viz-box-{}.pdf"
exp_dir_pattern = "exp[0-9][0-9][0-9]"


# Things we need from each experiment run
# name (dir), params that changed, values of changing parameters, metrics measured,

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


def create_bar(path, metric_name, params, settings, metric_values):
    x_range = range(0, len(settings))

    fig, ax = plt.subplots()
    ax.bar(x_range, metric_values, width=0.3)
    ax.set_ylabel(metric_name)
    ax.set_title('{} by\n{}'.format(metric_name, params))
    ax.set_xticks(x_range)
    ax.set_xticklabels(settings)

    filename = path / viz_file_pattern_bar.format(metric_name)
    print(str(filename))
    fig.savefig(str(filename))
    plt.close()


def create_bars(path, metric_info):
    metric_names = list(metric_info.values())[0][2].get_metrics()
    # Nasim: add list to it because in python 3 it returns a view, so it doesn't have indexing, you can't access it.

    for metric in metric_names:

        param_string = ""
        settings = []
        metric_vals = []

        for params, vals, log in metric_info.values():
            param_string = ', '.join(params)
            settings.append('\n'.join(vals))
            metric_vals.append(float(log.get_metric_values(metric)[-1]))

        create_bar(path, metric, param_string, settings, metric_vals)


def create_box(path, metric, params, settings, fold_values):
    fig, ax = plt.subplots()
    ax.boxplot(fold_values)
    ax.set_ylabel(metric)
    ax.set_xticklabels(settings)
    ax.set_title('{} distribution by\n{}'.format(metric, params))

    filename = path / viz_file_pattern_box.format(metric)

    fig.savefig(str(filename))
    plt.close()


def create_boxes(path, metric_info):
    metric_names = list(metric_info.values())[0][2].get_metrics()
    print(metric_names)
    for metric in metric_names:

        param_string = ""
        settings = []
        fold_vals = []

        for params, vals, log in metric_info.values():
            param_string = ', '.join(params)
            settings.append('\n'.join(vals))
            fold_vals.append([float(val) for val in log.get_metric_values(metric)[:-1]])

        create_box(path, metric, param_string, settings, fold_vals)


def create_graphics(config):
    files = config.get_files()
    metric_info = get_metric_info(config.get_files())

    create_bars(files.get_post_path(), metric_info)
    create_boxes(files.get_post_path(), metric_info)


def read_args():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(description='Generic post-processing script')
    parser.add_argument('conf', help='Path to configuration file')
    parser.add_argument('target', help='Experiment target')

    input_args = parser.parse_args()
    return vars(input_args)


if __name__ == '__main__':
    args = read_args()
    config = read_config_file(args['conf'], args['target'])

    print(f"librec-auto: Creating summary visualizations for {args['target']}")

    create_graphics(config)
