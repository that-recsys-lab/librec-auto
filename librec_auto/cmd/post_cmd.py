from librec_auto.cmd import Cmd
from librec_auto.util import Files
from librec_auto import ConfigCmd
import shutil
import os
import sys
import subprocess


class PostCmd(Cmd):

    def execute(self, config: ConfigCmd):
        self.status = Cmd.STATUS_INPROC
        files = config.get_files()

        target = files.get_exp_path()

        post_path = files.get_post_path()

        if not post_path.exists():
            print('librec-auto: post directory missing. Creating. ', target)
            os.makedirs(str(post_path))

        for script in self.collect_scripts(config):
            proc_spec = [sys.executable, script, files.get_post_path().absolute, files.get_result_path().absolute]
            print (f'librec-auto: Running post-processing script {script}')
            subprocess.call(proc_spec)

    def collect_scripts(self, config):
        post_xml = config.get_unparsed['post']
        script_stuff = post_xml['script']
        return [entry['#text'] for entry in script_stuff]
