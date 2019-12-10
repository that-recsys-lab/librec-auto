from librec_auto.cmd import Cmd
from librec_auto.util import Files, utils
from librec_auto import ConfigCmd
from pathlib import Path
import os
import sys
import subprocess


class PostCmd(Cmd):

    def __str__(self):
        return f'PostCmd()'

    def setup(self, args):
        pass

    def dry_run(self, config):
        print (f'librec-auto (DR): Running post command {self}')
        for script in self.collect_scripts(config):
            print (f'    Post script: {script}')

    def execute(self, config: ConfigCmd):
        self.status = Cmd.STATUS_INPROC
        files = config.get_files()

        target = files.get_exp_path()

        post_path = files.get_post_path()

        if not post_path.exists():
            print('librec-auto: post directory missing. Creating. ', target)
            os.makedirs(str(post_path))

        for script in self.collect_scripts(config):
            script_path = self.find_script_path(script, config)
            proc_spec = [sys.executable, script_path.absolute().as_posix(),
                         self._config.get_files().get_config_path().name,
                         config.get_target(),
                         files.get_post_path().absolute().as_posix()]
            print (f'librec-auto: Running post-processing script {proc_spec}')
            subprocess.call(proc_spec)

    def find_script_path(self, script, config):
        script_path = Path(script)
        if script_path.exists():
            return script_path
        else:
            return config.get_files().get_global_path() / "librec_auto/cmd/post" / script_path

    def collect_scripts(self, config):
        post_xml = config.get_unparsed('post')
        script_stuff = post_xml['script']
        return [utils.get_script_path(entry, 'post') for entry in utils.force_list(script_stuff)]
