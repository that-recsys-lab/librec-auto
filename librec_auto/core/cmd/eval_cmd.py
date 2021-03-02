from librec_auto.core import ConfigCmd
from librec_auto.core.cmd import Cmd


class EvalCmd(Cmd):
    def __init__(self, args, config):
        self._config = config
        self._args = args  # Evaluation arguments

    def __str__(self):
        return f'EvalCmd()'

    def setup(self, args):
        pass

    def dry_run(self):
        pass

    def execute(self, config: ConfigCmd):
        self._config = config
        self.status = Cmd.STATUS_INPROC

        metrics = config.get_python_metrics()
        cv_dirs = config.get_cv_directories()

        import pdb
        pdb.set_trace()
