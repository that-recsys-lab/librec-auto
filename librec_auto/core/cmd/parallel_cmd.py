from librec_auto.core.cmd import Cmd
from multiprocessing.dummy import Pool as ThreadPool
from librec_auto.core.util import Status


class ParallelCmd(Cmd):
    def __init__(self, cmds, threads):
        self._thread_count = threads
        if len(cmds) > 0:
            self.set_commands(cmds)
            self.status = Cmd.STATUS_CONFIG
        else:
            self._commands = []
        self._pool = None

    def __str__(self):
        return f'ParallelCmd({len(self._commands)} commands, {self._thread_count} threads)'

    def setup(self, args):
        for cmd in self._commands:
            cmd.setup(args)

    def set_commands(self, cmds):
        self._commands = cmds
        self.status = Cmd.STATUS_CONFIG

    def add_command(self, cmd):
        self._commands.append(cmd)

    def get_commands(self):
        return self._commands

    def dry_run(self, config):
        print(f"librec-auto (DR): Executing parallel, command {self}")
        self.status = Cmd.STATUS_INPROC
        self._pool = ThreadPool(self._thread_count)

        self._pool.map(lambda cmd: cmd.dry_run(config), self._commands)

        self._pool.close()
        self._pool.join()

        for cmd in self._commands:
            if cmd.status == Cmd.STATUS_ERROR:
                self.status = Cmd.STATUS_ERROR
                return
        self.status = Cmd.STATUS_COMPLETE

    def execute(self, config):
        self.status = Cmd.STATUS_INPROC
        self._pool = ThreadPool(self._thread_count)

        self._pool.map(lambda cmd: cmd.execute(config), self._commands)

        self._pool.close()
        self._pool.join()

        for cmd in self._commands:
            if cmd.status == Cmd.STATUS_ERROR:
                self.status = Cmd.STATUS_ERROR
                return
        self.status = Cmd.STATUS_COMPLETE
