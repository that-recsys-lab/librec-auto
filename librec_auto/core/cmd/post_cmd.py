from librec_auto.core.util.study_status import StudyStatus
from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files, utils, StudyStatus, ScriptFailureException, safe_run_subprocess
from librec_auto.core.util.xml_utils import single_xpath
from librec_auto.core import ConfigCmd
from pathlib import Path
import os
import sys
import subprocess
import re


class PostCmd(Cmd):

    POST_SCRIPT_PATH = "core/cmd/post"
    POST_ELEM_XPATH = '/librec-auto/post/script'

    def __init__(self):
        self._config = None

    def __str__(self):
        return f'PostCmd()'

    def setup(self, args):
        pass

    def dry_run(self, config):
        self._config = config
        print(f'librec-auto (DR): Running post command {self}')

        post_elems = config.get_xml().xpath(self.POST_ELEM_XPATH)

        for post_elem in post_elems:
            param_spec = utils.create_param_spec(post_elem)
            if single_xpath(post_elem,
                            "//param[@name='password']") is not None:
                param_spec = param_spec + ['--password=<password hidden>']
            script_path = utils.get_script_path(post_elem, 'post')

            print(f'\tPost script: {script_path}')
            print(f'\tParameters: {param_spec}')

    def execute(self, config: ConfigCmd):
        self._config = config
        self.status = Cmd.STATUS_INPROC
        files = config.get_files()

        StudyStatus(config)

        target = files.get_study_path()

        post_path = files.get_post_path()

        if not post_path.exists():
            print('librec-auto: post directory missing. Creating. ', target)
            os.makedirs(str(post_path))

        post_elems = config.get_xml().xpath(self.POST_ELEM_XPATH)

        for post_elem in post_elems:
            param_spec = utils.create_param_spec(post_elem)
            param_spec = self.handle_password(post_elem, config, param_spec)
            script_path = utils.get_script_path(post_elem, 'post')
            exec_path = config.get_files().get_study_path()

            proc_spec = [
                sys.executable,
                script_path.absolute().as_posix(),
                self._config.get_files().get_config_file_path().name
            ] + param_spec
            print(f'librec-auto: Running post-processing script {proc_spec}')
            # replace with safe_run_subprocess()
            # subprocess.call(proc_spec, cwd=str(exec_path.absolute()))
            run_script = safe_run_subprocess(proc_spec, str(exec_path.absolute()))
            script_name = re.split(r'/', str(script_path))[-1]
            if run_script != 0:
                self.status = Cmd.STATUS_ERROR
                raise ScriptFailureException(script_name, f"Post processing script at {str(script_path)} failed.", run_script)
        
        self.status = Cmd.STATUS_COMPLETE

    def handle_password(self, post_elem, config, param_spec):
        if single_xpath(post_elem, "param[@name='password']") is not None:
            val = config.get_key_password()
            if val:
                param_spec.append(f'--password={val}')
        return param_spec
