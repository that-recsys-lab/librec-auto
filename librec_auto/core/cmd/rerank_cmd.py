from librec_auto.core.util.utils import print_process_cli
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
    def __init__(self, exp_no=-1):
        self._files = None
        self._config = None
        self._exp_no = exp_no

    def __str__(self):
        return f'RerankCmd()'

    def show(self):
        print(str(self))

    def dry_run(self, config):
        self._files = config.get_files()
        self._config = config

        files = config.get_files()
        if files.get_exp_count() > 0:
            for i in range(0, files.get_exp_count()):
                sub_paths = files.get_exp_paths(i)
                script_elem = single_xpath(sub_paths.get_study_conf(),
                                           '/librec-auto/rerank/script')
                param_spec = create_param_spec(script_elem)
                script_path = get_script_path(script_elem, 'rerank')
                ref_path = sub_paths.get_ref_exp_name()
                result_path = sub_paths.get_path('result')

                original_path = self.find_original_results(result_path, script_path, sub_paths)

                print(
                    f'librec-auto (DR): Running re-ranking command {self} for {sub_paths.exp_name}'
                )

                proc_spec = [
                                sys.executable,
                                script_path.as_posix(),
                                self._config.get_files().get_config_file_path().name,
                                original_path.absolute().as_posix(),
                                sub_paths.get_path('result').absolute().as_posix()
                            ] + param_spec
                print_process_cli(proc_spec, str(self._config.get_files().get_study_path().absolute()))

                #print(f'\tRe-rank script: {script_path}')
                #print(f'\tParameters: {param_spec}')
                #if ref_path:
                #    print(f'\tResults from: {ref_path}')

    # TODO RB 2019-12-12 You can only have one re-ranking script. Others will be silently ignored. Should probably
    # have a warning for this.
    def execute(self, config: ConfigCmd):
        self.status = Cmd.STATUS_INPROC
        self._files = config.get_files()
        self._config = config

        if self._exp_no == -1:
            if self._files.get_exp_count() > 0:
                for i in range(0, self._files.get_exp_count()):
                    sub_path = self._files.get_exp_paths(i)
                    self.rerank(sub_path)
        else:
            sub_path = self._files.get_exp_paths(self._exp_no)
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

            original_path = self.find_original_results(result_path, script_path, sub_path)

            ret_val = self.run_script(script_path, sub_path, original_path,
                                      param_spec)
            
            script_name = script_elem.find('script-name').text

            if ret_val != 0:
                self.status = Cmd.STATUS_ERROR
                raise ScriptFailureException(script_name, f"Reranking script at {str(script_path)} failed.", ret_val)
                

            if len(script_elems) > 1:
                logging.warning(
                    'More than one re-ranking script found. Ignoring.')

    def find_original_results(self, result_path, script_path, sub_path):
        if not result_path.exists():
            raise ScriptFailureException('rerank', f'No results. Cannot rerank: {self._config.get_target()}')
        original_path = sub_path.get_path('original')
        # If original dir not empty, don't overwrite
        if not os.listdir(original_path):
            sub_path.results2original()  # and there are results here
        original_path = sub_path.get_path('original')

        return original_path

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

