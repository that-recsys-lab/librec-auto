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

    def __init__(self, no_java_flag):
        super().__init__()
        self._no_java_flag = no_java_flag

    def setup(self, args):
        pass

    def dry_run(self, config: ConfigCmd):
        print(f"librec-auto (DR): Executing setup command {self}")
        config.ensure_experiments()
        config.setup_exp_configs()

    def execute(self, config: ConfigCmd, startflag = None, exp_no = None):
        if not self._no_java_flag:
            ensure_java_version()
        else:
            logging.info("Java version checked not performed")
        config.ensure_experiments(exp_no)
        config.setup_exp_configs(startflag)

def ensure_java_version():
        java_dict = {
            'java': 1.8,
            'openjdk': 8.0
        }
        java_version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT) # returns bytestring
        java_version = java_version.decode("utf-8") # convert to regular string
        version_number_pattern = r'(.*) version \"(\d+\.\d+).\d+\"' # regex pattern matching
        version_name, version_number = re.search(version_number_pattern, java_version).groups() 
        logging.info(f'Java version detected: {version_name} {version_number}')
        try:
            if float(version_number) < java_dict[version_name]:
                raise JavaVersionException(version_name)
        except KeyError:
            logging.warning(f'{version_name} untested, please ensure compatibility with Java 8 or later.')
