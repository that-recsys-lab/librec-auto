from librec_auto.cmd import Cmd
from librec_auto.util import Files
from librec_auto.util.utils import safe_xml_path, extract_from_path
from librec_auto import ConfigCmd
import sys
import subprocess


class RerankCmd(Cmd):

    _files = None

    def __str__(self):
        return f'RerankCmd()'

    def setup(self, args):
        pass

    def dry_run(self, config):
        script = self.get_script(config)
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

        target = self._files.get_exp_path()

        result_path = self._files.get_result_path()

        if not result_path.exists():
            print('librec-auto: No results. Cannot rerank ', target)
        else:
            script = self.get_script(config)
            if self._files.get_sub_count() > 0:
                for i in range(0, self._files.get_sub_count()):
                    sub_paths = self._files.get_sub_paths(i)

                    print(f'librec-auto: Running re-ranking script {script} for {sub_paths.subexp_name}')
                    self.run_script(script, sub_paths)

    def run_script(self, script, sub_paths):
        # TODO: RB If rerank only, then leave original folder alone and delete results files
        sub_paths.results2original()
        proc_spec = [sys.executable, script, sub_paths.get_path('conf'),
                        self._files.get_original_path().absolute,
                        self._files.get_result_path().absolute]
        subprocess.call(proc_spec)

    def get_script(self, config):
        post_xml = config.get_unparsed('rerank')
        script_xml = post_xml['script']
        if '#text' in script_xml:
            return script_xml['#text']
        else:
            return None

