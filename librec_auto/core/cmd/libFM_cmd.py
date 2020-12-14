from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files, ExpPaths, Status
from librec_auto.core import ConfigCmd
from librec_auto.core.util.xml_utils import single_xpath
from librec_auto.core.util import Files, utils, build_parent_path, LibrecProperties, \
    xml_load_from_path, Library, LibraryColl, merge_elements, VarColl
import os
import os.path
from os import path
import subprocess
import shlex
import time
from pathlib import Path, WindowsPath
import sys
import pandas as pd
from numpy import loadtxt


class LibFMCmd(Cmd):
    POST_SCRIPT_PATH = "core/cmd/externalAlgo"
    POST_ELEM_XPATH = '/librec-auto/alg/script'
    _DEFAULT_WRAPPER_CLASS = "net.that_recsys_lab.auto.SingleJobRunner"

    def __str__(self):
        return f'LibFM(sub-exp: {self._sub_no}, command: {self._command})'

    def __init__(self, command, sub_no):
        super().__init__()
        self._files = None
        self._command = command
        self._sub_no = sub_no
        self._config: ConfigCmd = None
        self._exp_path: ExpPaths = None

    def setup(self, args):
        pass

    # 2020-01-06 RB Theoretically, subprocess.run is the right way to do this, but capturing the log output
    # seems to work more naturally with Popen. A mystery for future developers. Also, capture_output requires
    # Python 3.8, which may be too much to ask at this point.
    # proc = subprocess.run(cmd, capture_output=True

    def modify_file(self, target, libfm_filename, librec_filename, study_path):
        curr_path = study_path + "/" + target
        print(curr_path + "/data/" + libfm_filename)
        data = pd.read_csv(curr_path + "/data/" + libfm_filename, sep=",")
        #data = data.iloc[:, [0, 1, 2]]
        length = len(data.columns)
        columns = [*range(0, length)]
        data.columns = columns

        user_dict = {}
        count = 1
        for i in data[0]:
            if i not in user_dict:
                user_dict[i] = count
                count = count + 1

        item_dict = {}
        count = 1
        for i in data[1]:
            if i not in item_dict:
                item_dict[i] = count
                count = count + 1

        data.loc[:, 0] = data.apply(lambda x: user_dict[x[0]], axis=1)
        data.loc[:, 1] = data.apply(lambda x: item_dict[x[1]], axis=1)

        data.to_csv(curr_path + "/data/" + libfm_filename, header=None, index=False)
        df = data.iloc[:, [0, 1, 2]]
        df.to_csv(curr_path + "/data/" + librec_filename, header=None, index=False)
        print(f"Outer and Inner Dictionaries created. File modified and saved")

    def execute_librec(self):
        log_path = self._exp_path.get_log_path()

        # change working directory
        self._files = self._config.get_files()
        study_path = os.getcwd()
        f = open(str(log_path), 'w+')

        target = self._config.get_target()
        props = LibrecProperties(self._config._xml_input, self._files)
        librec_filename = props.get_property('data.input.path')
        libfm_filename = props.get_property('data-ext.input.path')
        split_count = props.get_property("data.splitter.cv.number")

        self.modify_file(target, libfm_filename, librec_filename, study_path)

        f.close()
        params = "python -m librec_auto run -t " + target
        os.system(params)

        f = open(str(log_path), 'w+')

        post_elems = self._config.get_xml().xpath(self.POST_ELEM_XPATH)
        for post_elem in post_elems:
            script_path = utils.get_script_path(post_elem, 'externalAlgo')
            print(script_path)
            proc_spec = [
                sys.executable,
                script_path.absolute().as_posix(),
                target,
                libfm_filename,
                study_path,
                split_count
            ]
            print('libFM: Running script {proc_spec}')
            subprocess.call(proc_spec, cwd=study_path)

        f.close()
        params1 = "python -m librec_auto eval -t " + target
        p = os.system(params1)

        if p.returncode < 0:
            self.status = Cmd.STATUS_ERROR
        else:
            self.status = Cmd.STATUS_COMPLETE

    def dry_run_librec(self):
        cmd = self.create_proc_spec()

        proc_spec = ' '.join(cmd)
        print(
            f'librec-auto (DR): Executing librec command: {self},  sub-exp: {self._exp_path.exp_name}, exec: {proc_spec}'
        )
        # Only for testing parallel function
        # time.sleep(1.0)

    def dry_run(self, config):
        self._config = config
        self._exp_path = config.get_files().get_exp_paths(self._sub_no)
        link = self._exp_path.get_ref_exp_name()
        if link and self._command == 'run':  # If the results are stored elsewhere
            # then we don't execute librec to generate
            # results
            print(
                f'librec-auto (DR): Skipping librec. Getting results from {link}'
            )
        else:  # We are running librec normally or we have
            # a link but we are evaluating the results
            self.dry_run_librec()

    def execute(self, config: ConfigCmd):
        self._config = config
        self._exp_path = config.get_files().get_exp_paths(self._sub_no)
        link = self._exp_path.get_ref_exp_name()
        if link and self._command == 'run':
            self.status = Cmd.STATUS_COMPLETE
        else:
            self.ensure_clean_log()
            # Status.save_status("Executing", self._sub_no, config, self._exp_path)
            if self._command == "eval":
                self.fix_list_length()
            self.execute_librec()
        Status.save_status("Completed", self._sub_no, config, self._exp_path)

    # Checks for any contents of split directory, which would have been removed by purging
    def split_exists(self):
        split_path = self._config.get_files().get_split_path()
        return split_path.exists() and any(os.scandir(split_path))

    # Checks for any contents of results directory, which would have been removed by purging
    def results_exist(self):
        sub_paths = self._config.get_files().get_exp_paths(self._sub_no)
        results_path = sub_paths.get_path('results')
        return any(os.scandir(results_path))

    # log file appends by default
    def ensure_clean_log(self):
        librec_log = log_path = self._exp_path.get_log_path()
        if librec_log.is_file():
            librec_log.unlink()

    def create_proc_spec(self):
        classpath = self._config.get_files().get_classpath()
        mainClass = self._DEFAULT_WRAPPER_CLASS
        confpath = self._exp_path.get_librec_properties_path()
        confpath_str = str(confpath)

        java_command = self.select_librec_action()
        if java_command is None:
            return []
        else:
            return [
                'java', '-cp', classpath, mainClass, confpath_str, java_command
            ]

    # 2019-11-23 RB Not sure if this step can be replaced by more checking when commands are created.
    def select_librec_action(self):
        expVal = self._exp_path.exp_name

        if self._command == 'split':
            # check if split exists, if so split command doesn't make sense. Does not purge here.
            if self.split_exists():
                print("Split already exists. Skipping.")
                return None
            else:
                return 'split'

        if self._command == 'eval':
            if self.results_exist():
                return 'reRunEval'
            else:  # No result file present, Then check if split exists
                if self.split_exists():
                    return 'exp-eval'
                else:
                    return 'full'

        if self._command == 'full':
            return 'full'

        if self._command == 'check':
            return 'check'
        else:
            return None
