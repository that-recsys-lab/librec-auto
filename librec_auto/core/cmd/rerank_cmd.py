from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files
from librec_auto.core.util.utils import create_param_spec, get_script_path
from librec_auto.core.util.xml_utils import single_xpath
from librec_auto.core import ConfigCmd
import sys
import subprocess
from lxml import etree
import logging


class RerankCmd(Cmd):

    def __init__(self):
        self._files = None
        self._config = None

    def __str__(self):
        return f'RerankCmd()'

    def setup(self, args):
        pass

    def dry_run(self, config):
        self._files = config.get_files()
        self._config = config

        files = config.get_files()
        if files.get_sub_count() > 0:
            for i in range(0, files.get_sub_count()):
                sub_path = files.get_sub_paths(i)
                script_elem = single_xpath(sub_path.get_exp_conf(), '/librec-auto/rerank/script')
                param_spec = create_param_spec(script_elem)
                script_path = get_script_path(script_elem, 'rerank')
                ref_path = sub_path.get_ref_exp_name()

                print(f'librec-auto (DR): Running re-ranking command {self} for {sub_path.subexp_name}')
                print(f'\tRe-rank script: {script_path}')
                print(f'\tParameters: {param_spec}')
                if ref_path:
                    print(f'\tResults from: {ref_path}')

    # TODO RB 2019-12-12 You can only have one re-ranking script. Others will be silently ignored. Should probably
    # have a warning for this.
    def execute(self, config: ConfigCmd):
        self.status = Cmd.STATUS_INPROC
        self._files = config.get_files()
        self._config = config

        if self._files.get_sub_count() > 0:
            for i in range(0, self._files.get_sub_count()):
                sub_path = self._files.get_sub_paths(i)
                self.rerank(sub_path)

    def rerank(self, sub_path):
        conf_xml = sub_path.get_exp_conf()
        script_elems = conf_xml.xpath('/librec-auto/rerank/script')
        if len(script_elems) > 0:
            script_elem = script_elems[0]
            param_spec = create_param_spec(script_elem)
            script_path = get_script_path(script_elem, 'rerank')
            result_path = sub_path.get_path('result')

            if not result_path.exists():
                print('librec-auto: No results. Cannot rerank ', self._config.get_target())
                return

            if not sub_path.get_ref_exp_name():            # If there is no ref, then LibRec was run
                sub_path.results2original()           # and there are results here
                original_path = sub_path.get_path('original')
            else:                                           # If there is a ref, the results are in
                ref_sub_path = sub_path.get_ref_sub_path()   # that experiment's directory
                original_path = ref_sub_path.get_path('original')

            print(f'librec-auto: Running re-ranking script {script_path} for {sub_path.subexp_name}')
            self.run_script(script_path, sub_path, original_path, param_spec)

            if len(script_elems) > 1:
                logging.warning('More than one re-ranking script found. Ignoring.')


    def run_script(self, script, sub_paths, original_path, param_spec):
        # TODO: RB If rerank only, then leave original folder alone and delete results files
        # TODO: RB If config file is in a non-standard place, I think this will fail. Maybe the sub-scripts
        # should get passed the same information as the original script when invoked?

        proc_spec = [sys.executable, script.as_posix(), self._config.get_files().get_config_path().name,
                     self._config.get_target(),
                     original_path.absolute().as_posix(),
                     sub_paths.get_path('result').absolute().as_posix()] + param_spec
        print("    Parameters: " + str(proc_spec))
        subprocess.call(proc_spec)
