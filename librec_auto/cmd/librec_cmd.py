from librec_auto.cmd import Cmd
from librec_auto.util import Files, SubPaths, Status
from librec_auto import ConfigCmd
import os
import subprocess
from pathlib import Path

class LibrecCmd (Cmd):

    _DEFAULT_WRAPPER_CLASS = "net.that_recsys_lab.auto.SingleJobRunner"
    _command = None

    def __init__(self, command, sub_no):
        self._command = command
        self._sub_no = sub_no
        self._config = None

    def execute_librec(self, exp_path: SubPaths):
        classpath = Files.get_classpath()
        mainClass = self._DEFAULT_WRAPPER_CLASS
        confpath = exp_path.get_path('conf')
        logpath = exp_path.get_path('log')

        java_command = self.select_librec_action(exp_path, self._command)
        cmd = ['java', '-cp', classpath, mainClass, str(confpath), java_command]
        f = open(str(logpath), 'w+')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        if p.returncode < 0:
            self.status = Cmd.STATUS_ERROR
        else:
            for line in p.stdout:
                f.write(str(line))

    def select_librec_action(self, exp_path: SubPaths, command):
        #path_str = str(path)
        expVal = exp_path.subexp_name

        if (command == 'split'):
            # check if split exists
            if self.split_exists():
                print("Split already exists. Skipping.")
                return None
            else:
                return 'split'

        if (command == 'eval'):
            if self.results_exist():
                return 're-eval'
            else:  # No result file present, Then check if split exists
                if self.split_exists():
                    return 'exp-eval'
                else:
                    return 'full'

        if (command == 'full'):
            return 'full'

    def execute(self, config: ConfigCmd):
        self._config = config
        sub_path = config.get_files().get_sub_paths(self._sub_no)

        var_params = config.var_params
        value_tuple = config.get_value_tuple(self._sub_no)

        self.save_properties_file(var_params, value_tuple, sub_path)

        self.ensure_clean_log()

        Status.save_status("Executing", self._sub_no, var_params, value_tuple, config, sub_path)
        self.execute_librec(sub_path)
        Status.save_status("Completed", self._sub_no, var_params, value_tuple, config, sub_path)

    def save_properties_file(self, params, values, sub_path):
        properties = self._config.get_prop_dict().copy()
        for key, value in zip(params, values):
            properties[key] = value  # Loop over all variables, value pairs
        # Various specific properties file hacks
        sub_path.add_to_config(properties, 'result')
        properties['dfs.split.dir'] = "split"

        self.write_key_value(properties, sub_path.get_librec_properties_path())

    def write_key_value(self, prop_dict, path):
        with path.open(mode="w") as fh:
            fh.write(u'# DO NOT EDIT\n# Properties file created by librec-auto\n')
            # for key, value in prop_dict.iteritems():
            for key, value in prop_dict.items():
                line = "{}:{}\n".format(key, value)  # type: str
                # fh.write(unicode(line))
                fh.write(str(line))

    # Checks for any contents of split directory, which would have been removed by purging
    def split_exists(self):
        split_path = self._config.get_split_path()
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
