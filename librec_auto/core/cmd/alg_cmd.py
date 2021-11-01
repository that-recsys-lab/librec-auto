from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files, ExpPaths, Status, safe_run_subprocess
from librec_auto.core import ConfigCmd
from pathlib import Path
from librec_auto.core.util.utils import create_param_spec, get_script_path
from librec_auto.core.util.xml_utils import single_xpath
from librec_auto.core.util.errors import *
import re
import sys
import logging


class AlgCmd(Cmd):
    def __str__(self):
        return f'AlgCmd(sub-exp: {self._sub_no})'

    def __init__(self, sub_no):
        super().__init__()
        self._sub_no = sub_no
        self._config: ConfigCmd = None
        self._exp_path: ExpPaths = None


    def setup(self, args):
        pass

    def dry_run(self, config):
        self.execute(dry_run=True)


    # script is going to need train file and test file. 
    
    def create_proc_spec(self, script_xml):

        # need to know what command type means
        script_path = get_script_path(script_xml, 'alg')
        if script_path:
            return ['python', script_path]
        else:
            return None
    
    def execute(self, config: ConfigCmd, dry_run=False):
        self._config = config
        self._exp_path = config.get_files().get_exp_paths(self._sub_no)
        self._files = config.get_files()
        if self._files.get_exp_count() > 0:
            for i in range(0, self._files.get_exp_count()):
                sub_path = self._files.get_exp_paths(i)
                self.execute_algorithm(sub_path, dry_run=dry_run)


    def get_all_splits(self):
        cv_data = []
        cv_dirs = self._config.get_cv_directories(absolute=True)
        for cv_dir in cv_dirs:
            cv_item = {}

            ans = re.search(r"cv_(\d+)", str(cv_dir))
            cv_item['split'] = int(ans.group(1))
            cv_item['train'] = cv_dir / self._files.DEFAULT_TRAIN_FILENAME
            cv_item['test'] = cv_dir / self._files.DEFAULT_TEST_FILENAME

            cv_data.append(cv_item)

        # cv_data = []
        # for dir_ in cv_dirs:
        #     for root, dirs, files in os.walk(dir_):
        #         cv_split_x = []
        #         for file in files:
        #             cv_split_x.append(root + "/" + file)
        #         cv_data.append(cv_split_x)
        return cv_data

    def execute_algorithm(self, sub_path, dry_run=False):
        conf_xml = sub_path.get_study_conf()
        script_elems = conf_xml.xpath('/librec-auto/alg/script')
        # cmd = self.create_proc_spec(script_elems)
        if len(script_elems) > 0:
            script_elem = script_elems[0]
            param_spec = create_param_spec(script_elem)
            script_path = get_script_path(script_elem, 'alg')
            cv_data = self.get_all_splits()
            
            print(
                f'librec-auto: Running algorithm script {script_path} for splits in {sub_path.exp_name}'
            )
            for cv_item in cv_data:
                train = cv_item['train']
                test = cv_item['test']
                split = cv_item['split']

                result_file = sub_path.get_path('result') / f"out-{split}.txt"

                ret_val = self.run_script(script_path, sub_path, train, test, result_file,
                                        param_spec, dry_run=dry_run)

                if ret_val != 0:
                    self.status = Cmd.STATUS_ERROR
                    script_name = script_elem.find('script-name').text
                    raise ScriptFailureException(script_name, f"Algorithm script at {str(script_path)} failed.", ret_val)
                else:
                    self.status = Cmd.STATUS_INPROC
            self.status = Cmd.STATUS_COMPLETE

        if len(script_elems) > 1:
            logging.warning(
                'More than one algorithm script found. Ignoring.')

    def run_script(self, script, sub_paths, training_set, test_set, result_file, param_spec,
                   dry_run=False):
        exec_path = self._config.get_files().get_study_path()

        proc_spec = [
            sys.executable,
            script.as_posix(),
            self._config.get_files().get_config_file_path().name,
            training_set.absolute().as_posix(),
            test_set.absolute().as_posix(),
            result_file.absolute().as_posix()
        ] + param_spec
        print("    Parameters: " + str(proc_spec))
        print("    Working directory: " + str(exec_path.absolute()))

        if dry_run:
            return 0
        else:
            return safe_run_subprocess(proc_spec, str(exec_path.absolute()))