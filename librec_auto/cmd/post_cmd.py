from librec_auto.cmd import Cmd
from librec_auto.util import Files, utils
from librec_auto import ConfigCmd
from pathlib import Path
import os
import sys
import subprocess


class PostCmd(Cmd):

    POST_SCRIPT_PATH = "librec_auto/cmd/post"

    _config = None

    def __str__(self):
        return f'PostCmd()'

    def setup(self, args):
        pass

    def dry_run(self, config):
        self._config = config
        print (f'librec-auto (DR): Running post command {self}')
        for script_path, params in config.collect_scripts('post'):
            if params is not None:
                param_spec = utils.create_param_spec(params)
            else:
                param_spec = []
            print (f'    Post script: {script_path}')
            print (f'\tParameters: {param_spec}')

    def execute(self, config: ConfigCmd):
        self._config = config
        self.status = Cmd.STATUS_INPROC
        files = config.get_files()

        target = files.get_exp_path()

        post_path = files.get_post_path()

        if not post_path.exists():
            print('librec-auto: post directory missing. Creating. ', target)
            os.makedirs(str(post_path))

        for script_path, params in config.collect_scripts('post'):
            if params is not None:
                param_spec = utils.create_param_spec(params)
            else:
                param_spec = []
            proc_spec = [sys.executable, script_path.absolute().as_posix(),
                         self._config.get_files().get_config_path().name,
                         config.get_target()] + param_spec
            print (f'librec-auto: Running post-processing script {proc_spec}')
            subprocess.call(proc_spec)
