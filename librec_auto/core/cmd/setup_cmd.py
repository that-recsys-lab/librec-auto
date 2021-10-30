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

    def setup(self, args):
        pass

    def dry_run(self, config: ConfigCmd):
        print(f"librec-auto (DR): Executing setup command {self}")
        config.ensure_experiments()
        config.setup_exp_configs()

    def execute(self, config: ConfigCmd, startflag = None, exp_no = None):
        # ensure_java_version()
        config.ensure_experiments(exp_no)
        config.setup_exp_configs(startflag)

def ensure_java_version():
        java_dict = {
            'java': 1.8,
            'openjdk': 8.0
        }
        java_version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT) # returns bytestring
        java_version = java_version.decode("utf-8") # convert to regular string
        version_number_pattern = r'(.*) version \"(\d+\.\d+).*\"' # regex pattern matching
        # version_number_pattern_alternate = r'(.*) version \"(\d+\.\d+).\d+\_\d+"' # regex pattern matching
        # print(java_version)
        # print(re.search(version_number_pattern, java_version))
        # print(re.search(version_number_pattern_alternate, java_version))
        version_name, version_number = 0,0

        if re.search(version_number_pattern, java_version) is not None:
            # print("if")
            version_name, version_number = re.search(version_number_pattern, java_version).groups() 

        # else:
        #     print("else")
        #     version_name, version_number = re.search(version_number_pattern_alternate, java_version).groups() 
        #     print(version_name, version_number)
        try:
            if float(version_number) < java_dict[version_name]:
                raise JavaVersionException(version_name)
        except KeyError:
            logging.warn(f'{version_name} untested, please ensure compatibility with Java 8 or later.')
