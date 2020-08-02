from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files
from librec_auto.core.util.utils import create_param_spec
from librec_auto.core import ConfigCmd
import sys
import subprocess


class RerankCmd(Cmd):

    _files = None
    _config = None

    def __str__(self):
        return f'RerankCmd()'

    def setup(self, args):
        pass

    def dry_run(self, config):
        script_data = config.collect_scripts('rerank')[0]
        files = config.get_files()
        if files.get_sub_count() > 0:
            for i in range(0, files.get_sub_count()):
                sub_paths = files.get_sub_paths(i)

                print(f'librec-auto (DR): Running re-ranking command {self} for {sub_paths.subexp_name}')
                print(f'\tRe-rank script: {script_data[0]}')
                print(f'\tParameters: {script_data[1]}')
        else:
            print(f'librec-auto (DR): Running re-ranking command {self} but no results to re-rank.')
            print(f'    Re-rank script: {script}')

    # TODO RB 2019-12-12 You can only have one re-ranking script. Others will be silently ignored. Should probably
    # have a warning for this.
    def execute(self, config: ConfigCmd):
        self.status = Cmd.STATUS_INPROC
        self._files = config.get_files()
        self._config = config
        script_data = config.collect_scripts('rerank')[0]
        script = script_data[0]
        param_spec = create_param_spec(script_data[1])

        target = self._files.get_exp_path()

        if self._files.get_sub_count() > 0:
            for i in range(0, self._files.get_sub_count()):
                sub_paths = self._files.get_sub_paths(i)
                result_path = sub_paths.get_path('result')

                if not result_path.exists():
                    print('librec-auto: No results. Cannot rerank ', target)
                else:
                    print(f'librec-auto: Running re-ranking script {script} for {sub_paths.subexp_name}')
                    self.run_script(script, sub_paths, param_spec)

    def run_script(self, script, sub_paths, param_spec):
        # TODO: RB If rerank only, then leave original folder alone and delete results files
        # TODO: RB If config file is in a non-standard place, I think this will fail. Maybe the sub-scripts
        # should get passed the same information as the original script when invoked?
        sub_paths.results2original()
        proc_spec = [sys.executable, script.as_posix(), self._config.get_files().get_config_path().name,
                     self._config.get_target(),
                     sub_paths.get_path('original').absolute().as_posix(),
                     sub_paths.get_path('result').absolute().as_posix()] + param_spec
        print("    Parameters: " + str(proc_spec))
        subprocess.call(proc_spec)
