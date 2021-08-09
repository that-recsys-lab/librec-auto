from abc import ABC, abstractmethod


class Cmd(ABC):

    STATUS_INIT = 0
    STATUS_CONFIG = 1
    STATUS_INPROC = 2
    STATUS_COMPLETE = 3
    STATUS_ERROR = -1

    def __init__(self):
        self.status = self.STATUS_INIT

    def __repr__(self):
        return "Cmd()"

    def __str__(self):
        return f"Cmd({type(self)})"

    @abstractmethod
    def setup(self, args):
        pass

    @abstractmethod
    def dry_run(self, config):
        print(f"librec-auto (DR): Executing command {self}")

    @abstractmethod
    def execute(self, config):
        pass


class SequenceCmd(Cmd):

    _commands = []

    def __str__(self):
        return f'SequenceCmd({len(self._commands)} commands)'

    def __init__(self, cmds):
        if len(cmds) > 0:
            self.set_commands(cmds)

    def setup(self, args):
        for cmd in self.commands:
            cmd.setup(args)

    def set_commands(self, cmds):
        self._commands = cmds
        self.status = Cmd.STATUS_CONFIG

    def add_command(self, cmd, pos=None):
        if isinstance(cmd, Cmd):
            self._commands.append(cmd)
        elif isinstance(cmd, list):
            if pos is not None:
                self._commands[pos:pos] = cmd
            else:
                self._commands.extend(cmd)


    def get_commands(self):
        return self._commands

    def dry_run(self, config):
        print(f"librec-auto (DR): Executing sequence command {self}")
        for cmd in self._commands:
            cmd.dry_run(config)

    def execute(self, config):
        self.status = Cmd.STATUS_INPROC
        for cmd in self._commands:
            cmd.execute(config)
            if cmd.status == Cmd.STATUS_ERROR:
                self.status = Cmd.STATUS_ERROR
                return
        self.status = Cmd.STATUS_COMPLETE
