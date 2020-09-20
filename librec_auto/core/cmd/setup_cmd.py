from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files, ExpPaths
from librec_auto.core import ConfigCmd
from librec_auto.core.util import confirm
import shutil
import os


class SetupCmd(Cmd):
    def __str__(self):
        return 'SetupCmd()'

    def setup(self, args):
        pass

    def dry_run(self, config):
        print(f"librec-auto (DR): Executing setup command {self}")
        config.ensure_experiments()
        config.setup_exp_configs()

    def execute(self, config: ConfigCmd):
        config.ensure_experiments()
        config.setup_exp_configs()
