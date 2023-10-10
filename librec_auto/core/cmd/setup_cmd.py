from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files, ExpPaths, JavaVersionException
from librec_auto.core import ConfigCmd
from librec_auto.core.util import confirm
import shutil
import logging
import subprocess
import re
import os


class SetupCmd(Cmd):
    def __str__(self):
        return 'SetupCmd()'

    def __init__(self, no_java_flag, startflag = False, exp_no = None):
        super().__init__()
        self._no_java_flag = no_java_flag
        self.startflag = startflag
        self.exp_no = exp_no

    def show(self):
        print(str(self))

    def dry_run(self, config: ConfigCmd):
        print(f"librec-auto (DR): Executing setup command {self}")
        config.ensure_experiments()
        config.setup_exp_configs()

    def execute(self, config: ConfigCmd):
        config.ensure_experiments(self.exp_no)
        print(self.startflag)
        config.setup_exp_configs(self.startflag)

def ensure_java_version():
        java_dict = {
            'java': 1.8,
            'openjdk': 8.0
        }
        java_version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT) # returns bytestring
        java_version = java_version.decode("utf-8") # convert to regular string

        try:
            version_number_pattern = r'(.*) version \"(\d+\.\d+)\..*' # regex pattern matching
            version_name, version_number = re.search(version_number_pattern, java_version).groups() 
            logging.info(f'Java version detected: {version_name} {version_number}')
            if float(version_number) < java_dict[version_name]:
                raise JavaVersionException(version_name)
        except (KeyError, TypeError, AttributeError):
            try:
                alt_java_dict = {
                    'java': 8
                }
                version_number_pattern2 = r'(java) (\d+)'
                version_name2, version_number2 = re.search(version_number_pattern2, java_version).groups()
                if float(version_number2) < alt_java_dict[version_name2]:
                    raise JavaVersionException(version_name2)
            except KeyError: 
                logging.warning(f'{version_name} untested, please ensure compatibility with Java 8 or later. Run \'-nj\' to disable.')
