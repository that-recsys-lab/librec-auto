from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files, ExpPaths, Status, safe_run_subprocess
from librec_auto.core import ConfigCmd
from pathlib import Path
from librec_auto.core.util.utils import create_param_spec, get_script_path
from librec_auto.core.util.xml_utils import single_xpath
from librec_auto.core.util.errors import *
import os
import sys
import subprocess
import logging

class AlgCmd(Cmd):


    def __str__(self):
        return f'AlgCmd(sub-exp: {self._sub_no}, command: {self._command})'

    def __init__(self, command, sub_no):
        self._command = command
        self._sub_no = sub_no
        self._config: ConfigCmd = None
        self._exp_path: ExpPaths = None

    # script is going to need train file and test file. 
    
    def create_proc_spec(self, script_xml):

        # need to know what command type means
        script_path = get_script_path(script_xml, 'alg')
        if script_path:
            return ['python', script_path]
        else:
            return None
    
    def execute(self, config: ConfigCmd):
        self._config = config
        self._exp_path = config.get_files().get_exp_paths(self._sub_no)
        self._files = config.get_files()
        if self._files.get_exp_count() > 0:
            for i in range(0, self._files.get_exp_count()):
                sub_path = self._files.get_exp_paths(i)
                self.execute_algorithm(sub_path)

    def get_all_splits(self):
        cv_dirs = self._config.get_cv_directories()
        cv_data = []
        for dir_ in cv_dirs:
            for root, dirs, files in os.walk(dir_):
                cv_split_x = []
                for file in files:
                    cv_split_x.append(root + "/" + file)
                cv_data.append(cv_split_x)
        return cv_data

    def execute_algorithm(self, sub_path):
        conf_xml = sub_path.get_study_conf()
        script_elems = conf_xml.xpath('/librec-auto/alg/script')
        # cmd = self.create_proc_spec(script_elems)
        if len(script_elems) > 0:
            script_elem = script_elems[0]
            param_spec = create_param_spec(script_elem)
            script_path = get_script_path(script_elem, 'alg')
            cv_data = self.get_all_splits()
            
            print(
                f'librec-auto: Running algorithm script {script_path} for {sub_path.exp_name}'
            )
            for i, split in enumerate(cv_data):
                train = ''
                test = ''
                for dataset in split:
                    if 'train' in dataset:
                        train = dataset
                    if 'test' in dataset:
                        test = dataset

                result_file = sub_path.get_path('result') / f"out-{i}.txt"

                ret_val = self.run_script(script_path, sub_path, train, test, result_file,
                                        param_spec)
                
                script_name = script_elem.find('script-name').text

                if ret_val != 0:
                    self.status = Cmd.STATUS_ERROR
                    raise ScriptFailureException(script_name, f"Algorithm script at {str(script_path)} failed.", ret_val)
                

        if len(script_elems) > 1:
            logging.warning(
                'More than one algorithm script found. Ignoring.')

    def run_script(self, script, sub_paths, training_set, test_set, result_file, param_spec):
        # TODO: RB If rerank only, then leave original folder alone and delete results files
        # TODO: RB If config file is in a non-standard place, I think this will fail. Maybe the sub-scripts
        # should get passed the same information as the original script when invoked?
        exec_path = self._config.get_files().get_study_path()

        proc_spec = [
            sys.executable,
            script.as_posix(),
            self._config.get_files().get_config_file_path().name,
            training_set,
            test_set,
            result_file.absolute().as_posix()
        ] + param_spec
        print("    Parameters: " + str(proc_spec))
        print("    Working directory: " + str(exec_path.absolute()))
        
        return safe_run_subprocess(proc_spec, str(exec_path.absolute()))