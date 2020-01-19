
import argparse
from pathlib import Path
from librec_auto import ConfigCmd
from librec_auto.util import LogFile
from librec_auto.util import SubPaths
import librec_auto.utils.util
import sys

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')  # For non-windowed plotting

viz_file_pattern_bar = "viz-bar-{}.pdf"
viz_file_pattern_box = "viz-box-{}.pdf"
exp_dir_pattern = "exp[0-9][0-9][0-9]"




# Things we need from each experiment run
# name (dir), params that changed, values of changing parameters, metrics measured,

def get_metric_info(path):
    metric_info = {}
    exp_paths = list(path.glob(exp_dir_pattern))
    exp_count = len(exp_paths)

    for exp_path in exp_paths:
        exp_name = exp_path.name
        status = utils.xml_load_from_path(exp_path / ".status")

        if status_completed(status):
            params = status_params(status)
            vals = status_vals(status)
            log = LogFile(ExpPaths(path, exp_name, create=False))

            metric_info[exp_name] = (params, vals, log)

    return metric_info


def create_bar(path, metric_name, params, settings, metric_values):
    x_range = range(0, len(settings))

    fig, ax = plt.subplots()
    ax.bar(x_range, metric_values, width=0.3)
    ax.set_ylabel(metric_name)
    ax.set_title('{} by\n{}'.format(metric_name, params))
    ax.set_xticks(x_range)
    ax.set_xticklabels(settings)

    # Nasim: if "viz" folder doesn't exist, create one.
    Path(path / "post").mkdir(parents=True, exist_ok=True)
    filename = path / "post" / viz_file_pattern_bar.format(metric_name)
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

    # Nasim: if the viz folder doesn't exist, make it.
    Path(path / "viz").mkdir(parents=True, exist_ok=True)
    filename = path / "viz" / viz_file_pattern_box.format(metric)

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


def create_graphics(path):
    metric_info = get_metric_info(path)

    create_bars(path, metric_info)
    create_boxes(path, metric_info)


if __name__ == '__main__':
    # to seehow you can pass the api key as a parameter here and run the algorithm
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="what the action applies to")

    args = parser.parse_args()
    dictargs = vars(args)

    target = dictargs['target']

    base_path = Path(target)
    print("librec-auto: Creating summary visualizations for", target)

    create_graphics(base_path)

    print("librec-auto: Visualizations created")