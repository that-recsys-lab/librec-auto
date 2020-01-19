from librec_auto.util.sub_paths import SubPaths
import re

class LogFile:

    _metrics = None
    _values = None
    _kcv = None
    _log_path = None

    def __str__(self):
        return f'LogFile({self._values}'

    def __init__(self, paths: SubPaths):
        self._metrics = []
        self._values = {}

        self._log_path = paths.get_path('log')

        self.parse_log()

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

    def parse_log(self):
        eval_pattern_str = r'.*Evaluator info:(.*)Evaluator is (\d+.?\d+)'
        kcv_pattern_str = r'.*Splitting .* on fold (\d+)'
#        kcv_pattern_str = r'.*Splitter info: .* times is (\d+)'
        final_pattern_str = r'.*Evaluator value:(.*)Evaluator is (\d+.?\d+)'

        eval_pattern = re.compile(eval_pattern_str)
        kcv_pattern = re.compile(kcv_pattern_str)
        final_pattern = re.compile(final_pattern_str)

        with open(str(self._log_path / SubPaths.DEFAULT_LOG_FILENAME), 'r', newline='\n') as fl:

            i = 0
            for ln in fl:
                i += 1
                m_eval = re.match(eval_pattern, ln)
                m_kcv = re.match(kcv_pattern, ln)
                m_final = re.match(final_pattern, ln)

                # A little bit of a hack. The average summary value is added at the end of the list
                if m_eval is not None or m_final is not None:
                    if m_eval is None:
                        m_eval = m_final
                    metric_name = m_eval.group(1)
                    metric_value = m_eval.group(2)
                    self.add_metric_value(metric_name, metric_value)

            if m_kcv is not None:
                self._kcv = m_kcv.group(1)

