from librec_auto.core.util import ExpPaths
import re
import os


# By default, the most recent one in the directory
class LogFile:
    def __str__(self):
        return f'LogFile({self._values}'

    def __init__(self, paths: ExpPaths):
        self._metrics = []
        self._values = {}

        self._log_path = self.newest_log(paths)
        self._time_stamp = self.extract_time_stamp(self._log_path.name)
        self._kcv = None

        self.parse_log()

    def newest_log(self, paths):
        log_dir = paths.get_path('log')
        print(log_dir)
        log_files = os.listdir(log_dir)
        newest_file = sorted(log_files, reverse=True)[0]
        return log_dir / newest_file

    def get_metric_values(self, metric):
        if metric in self._values:
            return self._values[metric]
        else:
            return []

    def get_metrics(self):
        return self._metrics

    def get_metric_count(self):
        return len(self._metrics)

    def add_metric_value(self, metric, value):
        if metric in self._metrics:
            self._values[metric].append(value)
        else:
            self._values[metric] = [value]
            self._metrics.append(metric)

    def get_kcv_count(self):
        return self._kcv

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
        eval_pattern_str = r'.*Evaluator info:(.*)Evaluator is (-?\d+.?\d+)'
        kcv_pattern_str = r'.*Splitting .* fold.*'
        #        kcv_pattern_str = r'.*Splitter info: .* times is (\d+)'
        final_pattern_str = r'.*Evaluator value:(.*)Evaluator is (-?\d+.?\d+)'

        eval_pattern = re.compile(eval_pattern_str)
        kcv_pattern = re.compile(kcv_pattern_str)
        final_pattern = re.compile(final_pattern_str)

        kcv_count = 0

        with open(str(self._log_path), 'r', newline='\n') as fl:

            i = 0
            for ln in fl:
                i += 1
                eval = re.match(eval_pattern, ln)
                kcv = re.match(kcv_pattern, ln)
                final = re.match(final_pattern, ln)

                if kcv is not None:
                    kcv_count += 1

                # A little bit of a hack. The average summary value is added at the end of the list
                if eval is not None or final is not None:
                    if eval is None:
                        eval = final
                    metric_name = eval.group(1)
                    metric_value = eval.group(2)
                    self.add_metric_value(metric_name, metric_value)

            self._kcv = kcv_count
