from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files
from librec_auto.core import ConfigCmd
from librec_auto.core.util import Status

# What to check for:
# 1. paths are legal (include paths to scripts). Include both "system" and user-defined
# 2. we have write permission to files and directories
# 3. no necessary element are missing: data, splitter, alg, metric
# 4. if optimize, must be upper/lower elements in alg. Must NOT be value elements
# 5. if library reference, the ref exists.
# 6. (eventually) XML validation against schema
# 7. (eventually) validate script parameters. scripts must conform.
# 8. (eventually) fix Java side so that check command doesn't load and only runs once.

class CheckCmd(Cmd):
    def __str__(self):
        return f"CheckCmd()"

    def setup(self, args):
        pass

    def dry_run(self, config):
        print(f'librec-auto (DR): Running check command {self}')

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
