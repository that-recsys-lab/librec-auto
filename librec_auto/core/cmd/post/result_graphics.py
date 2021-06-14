import argparse
from librec_auto.core import read_config_file
from librec_auto.core.util import Status
import webbrowser

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use('Agg')  # For non-windowed plotting

viz_file_pattern_bar = "viz-bar-{}.jpg"
viz_file_pattern_box = "viz-box-{}.jpg"
viz_html_filename = "viz.html"
exp_dir_pattern = "exp[0-9][0-9][0-9]"

# Things we need from each experiment run
# name (dir), params that changed, values of changing parameters, metrics measured,


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

def metric_values_float(log, metric):
    str_values = log.get_metric_values(metric)['cv_results']
    return [float(val) for val in str_values]

def create_bar(path, metric_name, params, settings, metric_values):
    x_range = range(0, len(settings))

    fig, ax = plt.subplots()
    ax.bar(x_range, metric_values, width=0.3)
    ax.set_ylabel(metric_name)
    ax.set_title('{} by\n{}'.format(metric_name, params))
    ax.set_xticks(x_range)
    ax.set_xticklabels(settings)

    filename = path / viz_file_pattern_bar.format(metric_name)
    fig.savefig(str(filename))
    plt.close()

    return filename


def create_bars(path, metric_info):
    metric_names = list(metric_info.values())[0][2].get_metrics()
    # Nasim: add list to it because in python 3 it returns a view, so it doesn't have indexing, you can't access it.

    bar_paths = []

    for metric in metric_names:

        param_string = ""
        settings = []
        metric_vals = []

        for params, vals, log in metric_info.values():
            param_string = ', '.join(params)
            settings.append('\n'.join(vals))
            metric_vals.append(np.average(metric_values_float(log, metric)))

        bar_paths.append(
            create_bar(path, metric, param_string, settings, metric_vals))

    return bar_paths


def create_box(path, metric, params, settings, fold_values):
    fig, ax = plt.subplots()
    ax.boxplot(fold_values)
    ax.set_ylabel(metric)
    ax.set_xticklabels(settings)
    ax.set_title('{} distribution by\n{}'.format(metric, params))

    filename = path / viz_file_pattern_box.format(metric)

    fig.savefig(str(filename))
    plt.close()
    return filename


def create_boxes(path, metric_info):
    metric_names = list(metric_info.values())[0][2].get_metrics()

    box_paths = []
    for metric in metric_names:

        param_string = ""
        settings = []
        fold_vals = []

        for params, vals, log in metric_info.values():
            param_string = ', '.join(params)
            settings.append('\n'.join(vals))
            metric_vals = metric_values_float(log, metric)
            fold_vals.append(metric_vals)

        box_paths.append(
            create_box(path, metric, param_string, settings, fold_vals))

    return box_paths


PAGE_TEMPLATE = '<html><h1>Study results</h1>{}</html>'
METRIC_TEMPLATE = '<h2>Metric: {}</h2>{}'
IMAGE_TEMPLATE = '<img src="{}" />'


def create_html(path, metric_info, bars, boxes):
    html = PAGE_TEMPLATE
    metric_chunks = []
    metric_names = list(metric_info.values())[0][2].get_metrics()

    if boxes is None:
        for name, bar in zip(metric_names, bars):
            images = IMAGE_TEMPLATE.format(bar.name)
            metric_chunks.append(METRIC_TEMPLATE.format(name, images))
    else:
        for name, bar, box in zip(metric_names, bars, boxes):
            images = IMAGE_TEMPLATE.format(bar.name) + IMAGE_TEMPLATE.format(
                box.name)
            metric_chunks.append(METRIC_TEMPLATE.format(name, images))

    output = html.format('\n'.join(metric_chunks))

    filename = path / viz_html_filename

    with open(filename, 'w') as out_file:
        out_file.write(output)

    return filename


def create_graphics(config, display):
    files = config.get_files()
    metric_info = get_metric_info(files)

    print("Post path")
    print(files.get_post_path())

    bars = create_bars(files.get_post_path(), metric_info)

    if config.cross_validation(
    ) > 1:  # Box plot only makes sense for cross-validation
        boxes = create_boxes(files.get_post_path(), metric_info)
    else:
        boxes = None

    if display:
        html_file = create_html(files.get_post_path(), metric_info, bars,
                                boxes)
        webbrowser.open('file://' + str(html_file.absolute()),
                        new=1,
                        autoraise=True)


def read_args():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(
        description='Generic post-processing script')
    parser.add_argument('conf', help='Path to configuration file')
    parser.add_argument('--browser',
                        help='Show graphics in browser',
                        choices=['true', 'false'])

    input_args = parser.parse_args()
    return vars(input_args)


if __name__ == '__main__':
    args = read_args()
    config = read_config_file(args['conf'], ".")

    print(f"librec-auto: Creating summary visualizations")

    display = args['browser'] == 'true'

    create_graphics(config, display)