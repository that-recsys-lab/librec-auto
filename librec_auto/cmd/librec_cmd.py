from librec_auto.cmd import Cmd
from librec_auto.util import Files, SubPaths, Status
from librec_auto import ConfigCmd
import os
import subprocess
import shlex
import  time
from pathlib import Path, WindowsPath

class LibrecCmd (Cmd):

    _DEFAULT_WRAPPER_CLASS = "net.that_recsys_lab.auto.SingleJobRunner"
    _command = None
    _sub_no = -1
    _config: ConfigCmd = None
    _sub_path: SubPaths = None

    def __str__(self):
        return f'LibrecCmd(sub-exp: {self._sub_no}, command: {self._command})'

    def __init__(self, command, sub_no):
        self._command = command
        self._sub_no = sub_no
        self._config = None

    def setup(self, args):
        pass

    # 2020-01-06 RB Theoretically, subprocess.run is the right way to do this, but capturing the log output
    # seems to work more naturally with Popen. A mystery for future developers. Also, capture_output requires
    # Python 3.8, which may be too much to ask at this point.
    # proc = subprocess.run(cmd, capture_output=True
    def execute_librec(self):
        cmd = self.create_proc_spec()

        if len(cmd) == 0:
            print ("librec-auto: Unknown command {self._command}. Skipping LibRec execution.")
            self.status = Cmd.STATUS_ERROR
            return

        print(f"librec-auto: Running librec. {cmd}")
        log_path = self._sub_path.get_path('log') / SubPaths.DEFAULT_LOG_FILENAME
        f = open(str(log_path), 'w+')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        for line in p.stdout:
            f.write(str(line, 'utf-8'))
            print(str(line))
        f.close()

        #p.wait()

        if type(p.returncode) is 'int' and p.returncode < 0:
            self.status = Cmd.STATUS_ERROR
        else:
            self.status = Cmd.STATUS_COMPLETE


    def dry_run_librec(self):
        cmd = self.create_proc_spec()

        proc_spec = ' '.join(cmd)
        print (f'librec-auto (DR): Executing librec command: {self},  sub-exp: {self._sub_path.subexp_name}, exec: {proc_spec}')
        # Only for testing parallel function
        # time.sleep(1.0)

    def dry_run(self, config):
        self._config = config

        self._sub_path = config.get_files().get_sub_paths(self._sub_no)

        var_params = config.var_params
        value_tuple = config.get_value_tuple(self._sub_no-1)

        self.dry_run_librec()
        for param, val in zip(var_params, value_tuple):
            print (f'    {param}: {val}')

    def execute(self, config: ConfigCmd):
        self._config = config

        self._sub_path = config.get_files().get_sub_paths(self._sub_no)

        var_params = config.var_params
        # If all parameters are fixed, there's only one experiment
        if len(var_params) == 0:
            value_tuple = []
        else:
            value_tuple = config.get_value_tuple(self._sub_no)

        self.save_properties_file(var_params, value_tuple)

        self.ensure_clean_log()

        Status.save_status("Executing", self._sub_no, var_params, value_tuple, config, self._sub_path)
        self.execute_librec()
        Status.save_status("Completed", self._sub_no, var_params, value_tuple, config, self._sub_path)

    def save_properties_file(self, params, values):
        properties = self._config.get_prop_dict().copy()
        for key, value in zip(params, values):
            properties[key] = value  # Loop over all variables, value pairs
        # Various specific properties file hacks
        self._sub_path.add_to_config(properties, 'result')
        properties['dfs.split.dir'] = "split"

        self.write_key_value(properties)

    def write_key_value(self, prop_dict):
        prop_path = self._sub_path.get_librec_properties_path()
        with prop_path.open(mode="w") as fh:
            fh.write(u'# DO NOT EDIT\n# Properties file created by librec-auto\n')
            # for key, value in prop_dict.iteritems():
            for key, value in prop_dict.items():
                line = "{}:{}\n".format(key, value)  # type: str
                fh.write(str(line))

    # Checks for any contents of split directory, which would have been removed by purging
    def split_exists(self):
        split_path = self._config.get_files().get_split_path()
        return any(os.scandir(split_path))

    # Checks for any contents of results directory, which would have been removed by purging
    def results_exist(self):
        sub_paths = self._config.get_files().get_sub_paths(self._sub_no)
        results_path = sub_paths.get_path('results')
        return any(os.scandir(results_path))

    # log file appends by default
    def ensure_clean_log(self):
        librec_log = Path(Files.LOG_PATH)
        if librec_log.is_file():
            librec_log.unlink()

    def create_proc_spec(self):
        classpath = self._config.get_files().get_classpath()
        mainClass = self._DEFAULT_WRAPPER_CLASS
        confpath = self._sub_path.get_librec_properties_path()
        confpath_str = str(confpath)

        java_command = self.select_librec_action()
        if java_command is None:
            return []
        else:
            return ['java', '-cp', classpath, mainClass, confpath_str, java_command]

    # 2019-11-23 RB Not sure if this step can be replaced by more checking when commands are created.
    def select_librec_action(self):
        expVal = self._sub_path.subexp_name

        if self._command == 'split':
            # check if split exists, if so split command doesn't make sense. Does not purge here.
            if self.split_exists():
                print("Split already exists. Skipping.")
                return None
            else:
                return 'split'

        if self._command == 'eval':
            if self.results_exist():
                return 're-eval'
            else:  # No result file present, Then check if split exists
                if self.split_exists():
                    return 'exp-eval'
                else:
                    return 'full'

        if self._command == 'full':
            return 'full'

        if self._command == 'check':
            return 'check'
        else:
            return None
