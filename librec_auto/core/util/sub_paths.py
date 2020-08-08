from pathlib import Path
import os
import glob
import shutil
import logging
from datetime import datetime

class SubPaths:
    """
    Represents the various directories and paths associated with a single sub-experiment

    - log
    - result
    - original (for re-ranking
    - conf
    """

    _LIBREC_PROPERTIES_FILE = 'librec.properties'
    DEFAULT_LOG_PATTERN = "librec-{}.log"

    _path_dict = None

    _prop_dict = {'log': 'dfs.log.dir',
#                 'split': 'dfs.split.dir',
                 'result': 'dfs.result.dir',
                  'conf': 'dfs.config.dir'}

    _sub_dirs = ['conf', 'log', 'result', 'original']

    subexp_name = None

    def __init__(self, base, subexp_name, create=True):
        self._path_dict = {}
        self.subexp_name = subexp_name

        subexp_path = base / subexp_name
        self.set_path('subexp', subexp_path)

        status_path = subexp_path / '.status'
        self.set_path('status', status_path)

        for subdir in self._sub_dirs:
            subdir_path = subexp_path / subdir
            self.set_path(subdir, subdir_path)

        if create:
            logging.info("Creating subexperiment: {}", subexp_name)
            subexp_path.mkdir(exist_ok=True)
            for subdir in self._sub_dirs:
                self.get_path(subdir).mkdir(exist_ok=True)

    def get_path(self, type):
        if type in self._path_dict:
            return self._path_dict[type]
        else:
            return None

    def get_librec_properties_path(self):
        return self.get_path('conf') / self._LIBREC_PROPERTIES_FILE

    def get_path_str(self, type):
        return self.get_path(type).as_posix()

    def get_path_platform(self, type):
        return str(self.get_path(type))

    def get_path_prop(self, type):
        return self._prop_dict[type]

    def set_path(self, type, path):
        self._path_dict[type] = path

    def set_path_from_string(self, type, path_str):
        self._path_dict[type] = Path(path_str)

    # Assumes path is set up
    def add_to_config(self, config, type):
        prop_name = self.get_path_prop(type)
        prop_val = self.get_path_str(type)
        config[prop_name] = prop_val

    def results2original(self):
        original_path = self.get_path('original')
        result_path = self.get_path('result')
        shutil.rmtree(original_path)
        original_path.mkdir()
        files = glob.glob((result_path / '*').as_posix())
        for file in files:
            shutil.copy2(file, original_path)

    def original2results(self):
        original_path = self.get_path('original')
        result_path = self.get_path('result')
        files = glob.glob((original_path / '*').as_posix())
        for file in files:
            shutil.copy2(file, result_path)
        shutil.rmtree(original_path)

    def get_log_path(self):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = SubPaths.DEFAULT_LOG_PATTERN.format(stamp)
        return self.get_path('log') / fname


