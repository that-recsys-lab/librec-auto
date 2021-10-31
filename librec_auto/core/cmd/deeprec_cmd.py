from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files, ExpPaths, Status
from librec_auto.core import ConfigCmd
from librec_auto.core.util.xml_utils import single_xpath
from librec_auto.core.util.utils import create_param_spec, get_script_path
import os
import subprocess
import shlex
import time
from pathlib import Path, WindowsPath

class DeeprecCmd(Cmd):

    def __str__(self):
        return f'DeeprecCmd(sub-exp: {self._sub_no}, command: {self._command})'

    def __init__(self, command, sub_no):
        self._train = '/Users/liuzijun1/Desktop/librec-auto/librec-auto-demo2020/data/split/cv_1/train.txt'
        self._test = '/Users/liuzijun1/Desktop/librec-auto/librec-auto-demo2020/data/split/cv_1/test.txt'
        self._result_file = "/Users/liuzijun1/Desktop/librec-auto/librec-auto-demo2020/demo02/exp00000/result/out1.txt"
        self._command = command
        self._sub_no = sub_no
        self._files = None
        self._config: ConfigCmd = None
        self._exp_path: ExpPaths = None

    def setup(self, args):
        pass

    def create_proc_spec(self):
        classpath = self._config.get_files().get_deeprec_classpath()
        config_xml = self._config.get_files().get_config_file_path()
        #script_xml = single_xpath(config_xml, '/librec-auto/algo/script')
        
        #pass config file

        python_command = self.select_deeprec_action()
        if python_command is None:
            return []
        else:
            return [
                'python', classpath, '--train', self._train, '--test', self._test, '--result_file', self._result_file
            ]

    def select_deeprec_action(self):
        if self._command == 'deep_algo':
            return 'deep_algo'

    def execute_deeprec(self, sub_path):
        conf_xml = sub_path.get_study_conf()
        script_elems = conf_xml.xpath('/librec-auto/alg/script')
        cmd = self.create_proc_spec()

        if len(cmd) == 0:
            print(
                "Deeprec: Unknown command {self._command}. Skipping Deeprec execution."
            )
            self.status = Cmd.STATUS_ERROR
            return
        print(f"DeepRec: Running DeepRec. {cmd}")
        if len(script_elems) > 0:
            script_elem = script_elems[0]
            param_spec = create_param_spec(script_elem)
            print (param_spec)
            script_path = get_script_path(script_elem, 'alg')
            study_path = self._files.get_study_path()
            result_path = sub_path.get_path('result')
        log_path = self._exp_path.get_log_path()
        #        print(f"librec-auto: Logging to {log_path}.")

        # change working directory
        _files = self._config.get_files()
        study_path = Path(_files.get_study_path())

        f = open(str(log_path), 'w+')

        '''
        Deep Rec algorithm
        '''
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             cwd=str(study_path.absolute()))

        for line in p.stdout:
            line_string = str(line, 'utf-8')
            f.write(line_string)
            print(line_string, end='')
        f.close()

        # p.wait()

        if type(p.returncode) == 'int' and p.returncode < 0:
            self.status = Cmd.STATUS_ERROR
        else:
            self.status = Cmd.STATUS_COMPLETE

    def dry_run_deeprec(self):
        cmd = self.create_proc_spec(config)

        proc_spec = ' '.join(cmd)
        print(
            f'Deeprec-auto (DR): Executing Deeprec command: {self},  sub-exp: {self._exp_path.exp_name}, exec: {proc_spec}'
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
                f'Deeprec-auto (DR): Skipping Deeprec. Getting results from {link}'
            )
        else:  # We are running deeprec normally or we have
            # a link but we are evaluating the results
            self.dry_run_deeprec()

        # log file appends by default
    def ensure_clean_log(self):
        librec_log = log_path = self._exp_path.get_log_path()
        if librec_log.is_file():
            librec_log.unlink()

    # Late night demo hack
    # The value of rec.recommender.ranking.topn must be the re-ranked list length
    # Must substitute here and re-write the configuration.
    def fix_list_length(self):
        config = self._config
        rerank_size_elem = single_xpath(
            config._xml_input,
            '/librec-auto/rerank/script/param[@name="max_len"]')

        if rerank_size_elem is None:
            return
        else:
            list_size_elem = single_xpath(config._xml_input,
                                          "/librec-auto/metric/list-size")
            list_size_elem.text = rerank_size_elem.text
            config.write_exp_configs()

    def execute(self, config: ConfigCmd):
        self._config = config
        self._exp_path = config.get_files().get_exp_paths(self._sub_no)
        self._files = config.get_files()
        if self._files.get_exp_count() > 0:
            for i in range(0, self._files.get_exp_count()):
                sub_path = self._files.get_exp_paths(i)
                self.execute_deeprec(sub_path)
        link = self._exp_path.get_ref_exp_name()
        if link and self._command == 'run':
            self.status = Cmd.STATUS_COMPLETE
        else:
            self.ensure_clean_log()

            # Status.save_status("Executing", self._sub_no, config,
            #                    self._exp_path)
            if self._command == "eval":
                self.fix_list_length()
            self.execute_deeprec(sub_path)

        # Status.save_status("Completed", self._sub_no, config, self._exp_path)







