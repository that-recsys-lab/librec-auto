from librec_auto.cmd import Cmd
from librec_auto.util import Files
from librec_auto.util.utils import safe_xml_path, extract_from_path
from librec_auto import ConfigCmd
import sys
import subprocess


class RerankCmd(Cmd):

    _files = None

    def execute(self, config: ConfigCmd):
        self.status = Cmd.STATUS_INPROC
        self._files = config.get_files()

        target = files.get_exp_path()

        result_path = files.get_result_path()

        if not result_path.exists():
            print('librec-auto: No results. Cannot rerank ', target)
        else:
            script = self.get_script(config)
            if self._files.get_sub_count() > 0:
                for i in range(1, self._files.get_sub_count() + 1):
                    sub_paths = self._files.get_sub_paths(i)

                    exp_str = sub_paths.get_path_str('subexp')
                    print(f'librec-auto: Running re-ranking script {script} for {subexp}')
                    self.run_script(script, sub_paths)

    def run_script(self, script, sub_paths):
        sub_paths.results2original()
        proc_spec = [sys.executable, script, sub_paths.get_path('conf'),
                        self._files.get_original_path().absolute,
                        self._files.get_result_path().absolute]
        subprocess.call(proc_spec)

    def get_script(self, config):
        post_xml = config.get_unparsed['rerank']
        script_xml = post_xml['script']
        if safe_xml_path(script_xml, [0, '#text']):
            return extract_from_path(script_xml, [0, '#text'])
