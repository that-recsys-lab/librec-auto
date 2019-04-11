import matplotlib
matplotlib.use('Agg') # For non-windowed plotting
import matplotlib.pyplot as plt
from log_file import LogFile
from exp_paths import ExpPaths

class DemoViz:

    _path = None
    _exp_count = None
    _variable_property = None
    _viz_file_pattern = "viz-{:02d}.pdf"
    _logs = None

    def __init__(self, path, variable_property):
        self._path = path
        self._exp_count = len(variable_property[1])
        self._variable_property = variable_property

        self._logs = [LogFile(ExpPaths(path, "exp{:03d}".format(i+1), create=False))
                      for i in range(0, self._exp_count)]


    def create(self):

        metric = 'RMSE'
        metric_values = [float(log.get_metric_values(metric)[-1]) for log in self._logs]
        x_range = range(0, self._exp_count)
        x_ticks = self._variable_property[1]

        fig, ax = plt.subplots()
        ax.bar(x_range, metric_values, width=0.3)
        ax.set_ylabel(metric)
        ax.set_title('{} by {}'.format(metric, self._variable_property[0]))
        ax.set_xticks(x_range)
        ax.set_xticklabels(x_ticks)

        filename = self._path / "viz" / self._viz_file_pattern.format(1)

        fig.savefig(str(filename))
        plt.close()

        fold_values = [[float(val) for val in log.get_metric_values(metric)[:-1]] for log in self._logs]

        fig, ax = plt.subplots()
        ax.boxplot(fold_values)
        ax.set_ylabel(metric)
        ax.set_xticklabels(x_ticks)
        ax.set_title('{} distribution by {}'.format(metric, self._variable_property[0]))

        filename = self._path / "viz" / self._viz_file_pattern.format(2)

        fig.savefig(str(filename))
        plt.close()

