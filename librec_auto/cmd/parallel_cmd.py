from librec_auto.cmd import Cmd
from multiprocessing.dummy import Pool as ThreadPool


class ParallelCmd(Cmd):

    _commands = []
    _pool = None
    _thread_count = 1

    def __init__(self, cmds, threads):
        _thread_count = threads
        if len(cmds) > 0:
            self.set_commands(cmds)
            self.status = Cmd.STATUS_CONFIG

    def setup (self, args):
        for cmd in self.commands:
            cmd.setup(args)

    def set_commands(self, commands):
        self.commands = cmds
        self.status = STATUS_CONFIG

    def get_commands(self):
        return self._commands

    def execute (self, config):
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

