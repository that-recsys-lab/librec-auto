from librec_auto.cmd import Cmd
from librec_auto.util import Files
from librec_auto import ConfigCmd
from librec_auto.util import LogFile
import sys
import subprocess


class StatusCmd(Cmd):

    def __str__(self):
        return f"StatusCmd()"

    def setup(self, args):
        pass

    def dry_run(self, config):
        print (f'librec-auto (DR): Running status command {self}')

    def execute(self, config: ConfigCmd):
        self.status = Cmd.STATUS_INPROC
        files = config.get_files()
        target = files.get_exp_path()
#        result_path = files.get_result_path()

        if files.get_sub_count()==0:
            print("librec-auto: No experiments found.")
        else:
            for sub_paths in files.get_sub_paths_iterator():
                status_path = sub_paths.get_path('status')
                if status_path.exists():
#                    self.print_status(status_path)
                    self.print_log_info(sub_paths)

        self.status = Cmd.STATUS_COMPLETE

    def print_log_info(self, sub_paths):
        log = LogFile(sub_paths)
        kcv_count = log.get_kcv_count()
        if kcv_count is None:
            self.print_metric_info(log, 1)
        else:
            self.print_metric_info(log, -1)

    def print_metric_info(self, log, idx):
        for metric_name in log.get_metrics():
            metric_value = log.get_metric_values(metric_name)[idx]
            print("    {}: {:.4f}".format(metric_name, float(metric_value)))
