import argparse
from pathlib2 import Path
from demo_viz import DemoViz
from config_simple import ConfigSimple
import matplotlib
matplotlib.use('Agg') # For non-windowed plotting
import matplotlib.pyplot as plt
from log_file import LogFile
from exp_paths import ExpPaths

viz_file_pattern = "viz-{:02d}.pdf"

def create(path, variable_property):

    for var, var_values in variable_property.iteritems():

        exp_count = len(var_values)

        logs = [LogFile(ExpPaths(path, "exp{:03d}".format(i + 1), create=False))
                  for i in range(0, exp_count)]

        metric = 'RMSE'
        metric_values = [float(log.get_metric_values(metric)[-1]) for log in logs]
        x_range = range(0, exp_count)
        x_ticks = var_values

        fig, ax = plt.subplots()
        ax.bar(x_range, metric_values, width=0.3)
        ax.set_ylabel(metric)
        ax.set_title('{} by {}'.format(metric, var))
        ax.set_xticks(x_range)
        ax.set_xticklabels(x_ticks)

        filename = path / "viz" / viz_file_pattern.format(1)

        fig.savefig(str(filename))
        plt.close()

        fold_values = [[float(val) for val in log.get_metric_values(metric)[:-1]] for log in logs]

        fig, ax = plt.subplots()
        ax.boxplot(fold_values)
        ax.set_ylabel(metric)
        ax.set_xticklabels(x_ticks)
        ax.set_title('{} distribution by {}'.format(metric, var))

        filename = path / "viz" / viz_file_pattern.format(2)

        fig.savefig(str(filename))
        plt.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="what the action applies to")

    args = parser.parse_args()
    dictargs = vars(args)

    target = dictargs['target']

    base_path = Path(target)

    config = ConfigSimple(base_path / "conf/config.xml")

    config.convert_properties()

    print "librec-auto: Creating summary visualizations for", target

    create(base_path, config.get_var_data())

    print "librec-auto: Visualizations created"