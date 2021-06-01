from librec_auto.core.cmd import Cmd
from librec_auto.core.util import Files, ExpPaths
from librec_auto.core import ConfigCmd
from librec_auto.core.util import confirm
import shutil
import os


class PurgeCmd(Cmd):
    def __str__(self):
        return f'PurgeCmd({self._type})'

    def __init__(self, type, no_ask=False):
        self._type = type
        self._no_ask = no_ask
        self._files = None

    def setup(self, args):
        pass

    def dry_run(self, config):
        print(f"librec-auto (DR): Executing purge command {self}")

    # 2021-05-31 TODO RB Need purge for the eval command
    def execute(self, config: ConfigCmd):
        self.status = Cmd.STATUS_INPROC
        self._files = config.get_files()

        if self._no_ask or self.purge_confirm():
            if self._type == "all" or self._type == 'split':
                self.purge_subexperiments()
                # self.purge_splits() # AS 10-23-20
                self.purge_post()

            if self._type == "results":
                self.purge_subexperiments()
                self.purge_post()

            if self._type == "rerank":
                self.purge_rerank()
                self.purge_post()

            if self._type == "post":
                self.purge_post()
        else:
            print("librec-auto: Skipping. No files deleted.")
        self.status = Cmd.STATUS_COMPLETE

    def purge_confirm(self):
        target = self._files.get_study_path()
        prompt_str = f"This will perform a purge of type {self._type} experiments and/or file splits in directory {target}"
        return confirm(prompt=prompt_str, resp=False)

    def purge_subexperiments(self):
        target = self._files.get_study_path()

        output_path = target / 'output.xml'
        if os.path.exists(output_path):
            os.remove(output_path)

        print("librec-auto: Purging sub-experiments", target)
        if self._files.get_exp_count() > 0:
            for sub_paths in self._files.get_exp_paths_iterator():
                exp_str = sub_paths.get_path_str('subexp')
                print("librec-auto: Deleting experiment directory:", exp_str)
                shutil.rmtree(exp_str)
        else:
            print("librec-auto: No experiments folders found in", target)

    # AS 10-23-20: Files.get_split_path() does not exist

    # def purge_splits(self):
    #     target = self._files.get_study_path()
    #     split_path = self._files.get_split_path()
    #     if split_path.exists():
    #         print("librec-auto: Deleting split directories", target)
    #         shutil.rmtree(split_path.as_posix())
    #     else:
    #         print("librec-auto: No split directories found in", target)

    def purge_post(self):
        target = self._files.get_study_path()
        post_path = self._files.get_post_path()

        if post_path.exists():
            print("librec-auto: Deleting post directory files", target)

            files = post_path.glob('*')
            for f in files:
                os.remove(str(f))
        else:
            print("librec-auto: Post directory missing", target)

    # TODO: 2019-12-06 RB The status file will be out of date.
    def purge_rerank(self):
        if self._files.get_exp_count() > 0:
            for sub_paths in self._files.get_exp_paths_iterator():
                exp_str = sub_paths.get_path_str('subexp')
                print("librec-auto: Deleting reranked results:", exp_str)
                sub_paths.original2results()
                # delete original?