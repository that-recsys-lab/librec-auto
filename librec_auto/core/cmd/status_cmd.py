from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files
from librec_auto.core import ConfigCmd
from librec_auto.core.util import Status


class StatusCmd(Cmd):
    def __str__(self):
        return f"StatusCmd()"

    def setup(self, args):
        pass

    def dry_run(self, config):
        print(f'librec-auto (DR): Running status command {self}')

    def execute(self, config: ConfigCmd):
        self.status = Cmd.STATUS_INPROC
        files = config.get_files()
        target = files.get_study_path()
        #        result_path = files.get_result_path()

        if files.get_exp_count() == 0:
            print("librec-auto: No experiments found.")
        else:
            for exp_paths in files.get_exp_paths_iterator():
                status = Status(exp_paths)
                print(status)

        self.status = Cmd.STATUS_COMPLETE
