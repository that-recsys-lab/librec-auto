from librec_auto.cmd import Cmd
from librec_auto.util import Files
from librec_auto.util.utils import safe_xml_path, extract_from_path
from librec_auto import ConfigCmd
import sys
import subprocess
from inspect import getsourcefile
from os.path import abspath
from pathlib import Path

class RerankCmd(Cmd):

    _files = None
    _config = None

    def __str__(self):
        return f'RerankCmd()'

    def setup(self, args):
        pass

    def dry_run(self, config):
        script = self.get_script_path(config)
        files = config.get_files()
        if files.get_sub_count() > 0:
            for i in range(0, files.get_sub_count()):
                sub_paths = files.get_sub_paths(i)

                print(f'librec-auto (DR): Running re-ranking command {self} for {sub_paths.subexp_name}')
                print(f'    Re-rank script: {script}')
        else:
            print(f'librec-auto (DR): Running re-ranking command {self} but no results to re-rank.')
            print(f'    Re-rank script: {script}')

    def execute(self, config: ConfigCmd):
        self.status = Cmd.STATUS_INPROC
        self._files = config.get_files()
        self._config = config
        script = self.get_script_path(config)

        target = self._files.get_exp_path()

        if self._files.get_sub_count() > 0:
            for i in range(0, self._files.get_sub_count()):
                sub_paths = self._files.get_sub_paths(i)
                result_path = sub_paths.get_path('result')

                if not result_path.exists():
                    print('librec-auto: No results. Cannot rerank ', target)
                else:
                    print(f'librec-auto: Running re-ranking script {script} for {sub_paths.subexp_name}')
                    self.run_script(script, sub_paths)

    def run_script(self, script, sub_paths):
        # TODO: RB If rerank only, then leave original folder alone and delete results files
        sub_paths.results2original()
        proc_spec = [sys.executable, script.as_posix(), sub_paths.get_path('conf'), self._config.get_target(),
                        sub_paths.get_path('original').absolute(),
                        sub_paths.get_path('result').absolute()]
        subprocess.call(proc_spec)

    # TODO: 2019-12-07 RB Needs to have an easy way to specify built-in reranking scripts. Maybe an attribute?
    def get_script_path(self, config):
        post_xml = config.get_unparsed('rerank')
        script_xml = post_xml['script']
        if script_xml['@lang'] != 'python3':
            print(f'librec-auto: Only Python3 scripts currently supported. Got {script_xml["@lang"]}.')
            return None
        if '@src' in script_xml:
            if script_xml['@src'] == 'system':
                script_path = Path(abspath(getsourcefile(lambda:0))).parent / 'rerank'
            else:
                script_path = script_xml['@src']
        if '#text' in script_xml:
            return script_path / script_xml['#text']
        else:
            return None

