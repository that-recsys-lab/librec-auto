from collections import defaultdict
from librec_auto.core.util import ExpPaths
import re
import os


class LogFile:
    """
    Uses pattern matching to create an object out of the librec log files
    
    By default, this uses the most recent log file in the directory.
    """
    _LOG_FILE_RE = r'librec-\d+_\d+.log'

    def __str__(self):
        return f'LogFile({self._values}'

    def __init__(self, paths: ExpPaths, exp_ran=True):
        self._metrics = []
        self._values = {}

        # adding a flag will prevent newest_log from throwing an error
        # but parse_log can't work unless _log_path is set
        self._log_path = self.newest_log(paths)
        self._time_stamp = self.extract_time_stamp(self._log_path.name)
        self._kcv_count = 1  # one-indexed

        self._err_msgs = defaultdict(list)

        self.parse_log()

    def newest_log(self, paths):
        log_dir = paths.get_path('log')
        log_dir_files = os.listdir(log_dir)
        log_pat = re.compile(self._LOG_FILE_RE)

        log_files = list(filter(log_pat.match, log_dir_files))
        newest_file = sorted(log_files, reverse=True)[0]
        return log_dir / newest_file

    def get_all_values(self):
        return self._values

    def get_metric_values(self, metric):
        if metric in self._values:
            return self._values[metric]
        else:
            return []

    def get_metrics(self):
        return self._metrics

    def get_metric_count(self):
        return len(self._metrics)

    def add_metric_value(self, metric: str, value: str):
        """Adds the values from a metric to the class variables

        Args:
            metric (str): The name of the metric to be added
            value (str): The value for that metric
        """
        if metric in self._metrics:
            # append the value to the existing values list
            self._values[metric]['cv_results'].append(value)
        else:
            # add the value as a one item list at the metric key in _values
            self._values[metric] = {}
            self._values[metric]['cv_results'] = [value]
            # add the metric to the list of metrics
            self._metrics.append(metric)

    def add_metric_average(self, metric: str, value: str):
        """Adds the average result for a metric to _values

        Args:
            metric (str): The name of the metric to be added
            value (str): The average value for that metric across all folds
        """
        self._values[metric]['average_result'] = value
        if metric not in self._metrics:
            # add the metric to the list of metrics
            self._metrics.append(metric)

    def get_kcv_count(self):
        return self._kcv_count

    def get_time_stamp(self):
        return self._time_stamp

    def extract_time_stamp(self, filename):
        file_pattern_str = r'librec-(\d+_\d+).log'
        file_pattern = re.compile(file_pattern_str)
        match = re.match(file_pattern, filename)
        if match is not None:
            return match.group(1)
        else:
            return None

    def parse_log(self):
        """Parses librec logs

        Extracts the following:

        * Evaluator info (result metrics)
        * The number of CV folds
        * Evaluator values
        * Exceptions from librec log
        * Errors from librec log 
        """
        evaluator_pattern_str = r'.*Evaluator info:([A-z]*) is (-?[0-9.]*)'
        kcv_pattern_str = r'.*TextDataConvertor: Dataset: \[.+split/cv_(\d+)/test.txt\]'
        # Old pattern
        # kcv_pattern_str = r'.*Splitting training and testing with [.0-9]*% ratio on fold ([0-9]*)'
        final_pattern_str = r'.*Evaluator value:([A-z]*) is (-?[0-9.]*)'
        exception_pattern_str = r'^Exception in thread'
        error_pattern_str = r'^prog\.java:\d*: error:'

        evaluator_pattern = re.compile(evaluator_pattern_str)
        kcv_pattern = re.compile(kcv_pattern_str)
        final_pattern = re.compile(final_pattern_str)
        exception_pattern = re.compile(exception_pattern_str)
        error_pattern = re.compile(error_pattern_str)

        fold_count = 1

        with open(str(self._log_path), 'r', newline='\n') as log_file:
            for line_number, line in enumerate(log_file):
                evaluator = re.match(evaluator_pattern, line)
                kcv = re.match(kcv_pattern, line)
                final = re.match(final_pattern, line)
                exception = re.match(exception_pattern, line)
                error = re.match(error_pattern, line)

                if kcv is not None:
                    # update kcv_count from the splitting pattern
                    fold_count = int(kcv.group(1))

                if evaluator is not None:
                    metric_name = evaluator.group(1)
                    metric_value = evaluator.group(2)
                    self.add_metric_value(metric_name, metric_value)

                if final is not None:
                    metric_name = final.group(1)
                    metric_value = final.group(2)
                    self.add_metric_average(metric_name, metric_value)

                if exception is not None:
                    self._err_msgs['LibRec'].append((line_number+1, line))

                if error is not None:
                    self._err_msgs['LibRec'].append((line_number+1, line))

            self._kcv_count = fold_count  # one-indexed
