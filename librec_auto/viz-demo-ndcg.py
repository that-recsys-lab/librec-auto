import argparse
from pathlib2 import Path
from config_simple import ConfigSimple

import matplotlib
matplotlib.use('Agg') # For non-windowed plotting
import matplotlib.pyplot as plt
import utils
from log_file import LogFile
from exp_paths import ExpPaths

viz_file_pattern_bar = "viz-bar-{}.pdf"
viz_file_pattern_box = "viz-box-{}.pdf"
exp_dir_pattern = "exp[0-9][0-9][0-9]"

# Decoding the status. Should be a separate class.
def status_completed(status):
    msg = utils.extract_from_path(status, ['librec-auto-status', 'message'])
    return msg == 'Completed'


def status_params(status):
    param_specs = utils.force_list(utils.extract_from_path(status, ['librec-auto-status', 'param']))

    return [spec['name'] for spec in param_specs]


def status_vals(status):
    param_specs = utils.force_list(utils.extract_from_path(status, ['librec-auto-status', 'param']))

    return [spec['value'] for spec in param_specs]



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

    filename = path / "viz" / viz_file_pattern_bar.format(metric_name)

    fig.savefig(str(filename))
    plt.close()


def create_bars(path, metric_info):

    metric_names = metric_info.values()[0][2].get_metrics()

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

    filename = path / "viz" / viz_file_pattern_box.format(metric)

    fig.savefig(str(filename))
    plt.close()

def create_boxes(path, metric_info):

    metric_names = metric_info.values()[0][2].get_metrics()

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

    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="what the action applies to")

    args = parser.parse_args()
    dictargs = vars(args)

    target = dictargs['target']

    base_path = Path(target)

    print "librec-auto: Creating summary visualizations for", target

    create_graphics(base_path)

    print "librec-auto: Visualizations created"