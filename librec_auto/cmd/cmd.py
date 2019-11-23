from abc import ABC


class Cmd(ABC):

    STATUS_INIT = 0
    STATUS_CONFIG = 1
    STATUS_INPROC = 2
    STATUS_COMPLETE = 3
    STATUS_ERROR = -1

    status = STATUS_INIT

    def __repr__(self):
        return "Cmd()"

    @abstractmethod
    def setup (self, args):
        pass

    @abstractmethod
    def execute (self, config):
        pass

class SequenceCmd(Cmd):

    _commands = []

    def __init__(self, cmds):
        if len(cmds) > 0:
            self.set_commands(cmds)

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
        for cmd in self._commands:
            cmd.execute(config)
            if cmd.status == Cmd.STATUS_ERROR:
                self.status = Cmd.STATUS_ERROR
                return
        self.status = Cmd.STATUS_COMPLETE
