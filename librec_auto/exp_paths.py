import pathlib2

class ExpPaths:
    _path_dict = None

    _prop_dict = {'log': 'dfs.log.dir',
                 'split': 'dfs.split.dir',
                 'result': 'dfs.result.dir',
                  'conf': 'dfs.config.dir'}

    _sub_dirs = ['conf', 'log', 'result']

    def __init__(self, base, exp_name, create=True):
        self._path_dict = {}

        exp_path = base / exp_name
        self.set_path('exp', exp_path)

        status_path = exp_path / '.status'
        self.set_path('status', status_path)

        for sub in self._sub_dirs:
            sub_path = exp_path / sub
            self.set_path(sub, sub_path)

        if create:
            print ("exp_path: ", exp_path)
            exp_path.mkdir(exist_ok=True)
            for sub in self._sub_dirs:
                self.get_path(sub).mkdir(exist_ok=True)

    def get_path(self, type):
        if type in self._path_dict:
            return self._path_dict[type]
        else:
            return None

    def get_path_str(self, type):
        return self.get_path(type).as_posix()

    def get_path_platform(self, type):
        return str(self.get_path(type))

    def get_path_prop(self, type):
        return self._prop_dict[type]

    def set_path(self, type, path):
        self._path_dict[type] = path

    def set_path_from_string(self, type, path_str):
        self._path_dict[type] = pathlib2.Path(path_str)

    # Assumes path is set up
    def add_to_config(self, config, type):
        prop_name = self.get_path_prop(type)
        prop_val = self.get_path_str(type)
        config[prop_name] = prop_val
