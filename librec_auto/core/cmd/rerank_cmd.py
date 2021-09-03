from librec_auto.core.util.study_status import check_output_xml
import sys
import os
import subprocess
from subprocess import CalledProcessError, DEVNULL
from lxml import etree
import logging

from librec_auto.core import ConfigCmd
from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files, safe_run_subprocess
from librec_auto.core.util.utils import create_param_spec, get_script_path
from librec_auto.core.util.xml_utils import single_xpath
from librec_auto.core.util.errors import *


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
        if files.get_exp_count() > 0:
            for i in range(0, files.get_exp_count()):
                sub_path = files.get_exp_paths(i)
                script_elem = single_xpath(sub_path.get_study_conf(),
                                           '/librec-auto/rerank/script')
                param_spec = create_param_spec(script_elem)
                script_path = get_script_path(script_elem, 'rerank')
                ref_path = sub_path.get_ref_exp_name()

                print(
                    f'librec-auto (DR): Running re-ranking command {self} for {sub_path.exp_name}'
                )
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

        if self._files.get_exp_count() > 0:
            for i in range(0, self._files.get_exp_count()):
                sub_path = self._files.get_exp_paths(i)
                self.rerank(sub_path)

    def rerank(self, sub_path):
        conf_xml = sub_path.get_study_conf()
        script_elems = conf_xml.xpath('/librec-auto/rerank/script')
        if len(script_elems) > 0:
            script_elem = script_elems[0]
            param_spec = create_param_spec(script_elem)
            script_path = get_script_path(script_elem, 'rerank')
            study_path = self._files.get_study_path()
            result_path = sub_path.get_path('result')

            if not sub_path.get_ref_exp_name(
            ):  # If there is no ref, then LibRec was run
                if not result_path.exists():
                    print('librec-auto: No results. Cannot rerank ',
                          self._config.get_target())
                    return
                original_path = sub_path.get_path('original')
                # If original dir not empty, don't overwrite
                if not os.listdir(original_path):
                    sub_path.results2original()  # and there are results here
                original_path = sub_path.get_path('original')
            else:  # If there is a ref, the results are in
                ref_sub_path = sub_path.get_ref_exp_path(
                )  # that experiment's directory
                original_path = ref_sub_path.get_path('original')
                result_path.mkdir(
                    exist_ok=True)  # script needs a place for results
            print(
                f'librec-auto: Running re-ranking script {script_path} for {sub_path.exp_name}'
            )
    
            ret_val = self.run_script(script_path, sub_path, original_path,
                                      param_spec)
            
            script_name = script_elem.find('script-name').text

            if ret_val != 0:
                self.status = Cmd.STATUS_ERROR
                raise ScriptFailureException(script_name, f"Reranking script at {str(script_path)} failed.", ret_val)
                

            if len(script_elems) > 1:
                logging.warning(
                    'More than one re-ranking script found. Ignoring.')

    def run_script(self, script, sub_paths, original_path, param_spec):
        # TODO: RB If rerank only, then leave original folder alone and delete results files
        # TODO: RB If config file is in a non-standard place, I think this will fail. Maybe the sub-scripts
        # should get passed the same information as the original script when invoked?
        exec_path = self._config.get_files().get_study_path()

        proc_spec = [
            sys.executable,
            script.as_posix(),
            self._config.get_files().get_config_file_path().name,
            original_path.absolute().as_posix(),
            sub_paths.get_path('result').absolute().as_posix()
        ] + param_spec
        print("    Parameters: " + str(proc_spec))
        print("    Working directory: " + str(exec_path.absolute()))
        
        return safe_run_subprocess(proc_spec, str(exec_path.absolute()))
