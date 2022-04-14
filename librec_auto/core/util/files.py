from pathlib import Path
import hashlib
import inspect
import librec_auto
from librec_auto.core.util.utils import force_path
from librec_auto.core.util.xml_utils import xml_load_from_path, single_xpath
from collections import OrderedDict
import glob
import shutil
import logging
import os
from datetime import datetime
import os


class Files:
    """
    This class encapsulates the file system for librec-auto.

    The files for librec-auto can be stored in a number of possible locations:
    - global location: determined by the install location of librec-auto
    - rules-specific location: determined by the location of a rules directory [Not implemented]
    - user-specific location: associated with the user's home directory [Not implemented]
    - experiment-specific location: in a directory associated with a specific experiment.

    These are the types of files that are managed:
    - configuration files (XML). Stores information about how experiments are configured.
    - properties files (key=value format). Generated from configuration files for input to librec
    - split files (UIR or UIRT format). Generated by separating input rules files into different test/training splits
    - experiment logs (csv files). Content is algorithm-specific. Generated by a run of an experiment

    NOTE: User directory is currently unused.
    """

    _DEFAULT_GLOBAL_DIR_STR = inspect.getfile(librec_auto)

    _DEFAULT_CONFIG_DIR_NAME = "conf"
    _DEFAULT_RULES_DIR_NAME = "rules"
    _DEFAULT_LIB_DIR_NAME = "librec_auto/library"
    _DEFAULT_RES_DIR_NAME = "result"
    _DEFAULT_DATA_DIR_NAME = "data"
    _DEFAULT_JAR_DIR_NAME = "librec_auto/jar"
    _DEFAULT_POST_DIR_NAME = "post"
    _DEFAULT_LIBRARY_DIR_NAME = "lib"
    _EXP_DIR_FORMAT = "exp{:05d}"
    _EXP_DIR_PATTERN = "exp(\d+)"
    _OUTPUT_FILE_NAME = "output.xml"

    DEFAULT_PROP_FILE_NAME = "librec.properties"
    _DEFAULT_LA_JAR = "auto.jar"
    _DEFAULT_RULES_FILE = "librec_auto/rules/element-rules.xml"

    DEFAULT_CONFIG_FILENAME = "config.xml"
    DEFAULT_REF_EXP_FILENAME = "ref_exp.txt"
    DEFAULT_TRAIN_FILENAME = "train.txt"
    DEFAULT_TEST_FILENAME = "test.txt"

    _DEFAULT_SPLIT_DIR_NAME = "split"

    def __init__(self):
        self._config_dir_path = Path(self._DEFAULT_CONFIG_DIR_NAME)
        self._data_dir_path = Path(self._DEFAULT_DATA_DIR_NAME)
        self._jar_dir_path = Path(self._DEFAULT_JAR_DIR_NAME)
        self._post_dir_path = Path(self._DEFAULT_POST_DIR_NAME)
        self._lib_dir_path = Path(self._DEFAULT_LIBRARY_DIR_NAME)
        self._exp_path_dict = OrderedDict()
        

        module_init_path = Path(Files._DEFAULT_GLOBAL_DIR_STR).parent
        self._global_path = module_init_path.parent

        self._split_dir_path = Path(self._DEFAULT_SPLIT_DIR_NAME)

    # Paths related to the librec installation
    def get_global_path(self):
        return self._global_path

    def set_global_path(self, path):
        self._global_path = Path(path)

    def get_data_path(self):
        return self.get_study_path() / self._data_dir_path

    def set_data_path(self, config_xml):
        data_dir_elem = single_xpath(config_xml, '/librec-auto/data/data-dir')
        if data_dir_elem is None:
            logging.warning("Configuration file missing data-dir element. Assuming 'data'.")
        else:
            self._data_dir_path = data_dir_elem.text

    def get_rules_path(self):
        return self.get_global_path() / self._DEFAULT_RULES_FILE

    def get_lib_path(self):
        return self.get_global_path() / self._DEFAULT_LIB_DIR_NAME

    def get_jar_path(self):
        return self.get_global_path() / self._jar_dir_path

    def get_classpath(self):
        return (self.get_jar_path() /
                self._DEFAULT_LA_JAR).absolute().as_posix()

    # Paths related to the current study
    def get_study_path(self):
        return self._study_path

    def get_status_path(self):
        return self._study_path / self._OUTPUT_FILE_NAME

    def get_config_file_path(self):
        return self._study_path / self._config_dir_path / self._config_file_name

    def get_config_dir_path(self):
        return self._study_path / self._config_dir_path

    def set_post_path(self, path):
        self._post_dir_path = Path(path)

    def get_post_path(self):
        return self._study_path / self._post_dir_path

    def get_split_path(self):
        return self._data_dir_path / self._split_dir_path

    def set_study_path(self, path):
        self._study_path = Path(path)

    def set_config_file(self, filename):
        self._config_file_name = Path(filename)

    def create_temp_dir(self):
        path = str(self._study_path / 'temp')
        try:
            os.mkdir(path)
        except FileExistsError:
            logging.info("temporary directory already created, removing and recreating")
            shutil.rmtree(path)
            os.mkdir(path)

    
    def get_temp_dir_path(self):
        return self._study_path / 'temp'


    # Access to experiments within the current study
    @staticmethod
    def get_exp_name(count):
        if type(count) is str:
            count = int(count)
        return Files._EXP_DIR_FORMAT.format(count)

    def detect_exp_path(self, exp_no):
        return (self.get_study_path() / self.get_exp_name(exp_no)).exists()

    def detect_exp_paths(self, count=0):
        exp_count = 0
        while self.detect_exp_path(exp_count):
            self._exp_path_dict[exp_count] = ExpPaths(
                self, self.get_exp_name(exp_count), create=False)
            exp_count += 1
        if exp_count != count:
            print(
                f'librec-auto: Expecting {count} existing experiment directories in {self.get_study_path()}. Found {exp_count}.'
            )

    def create_exp_paths(self, tuple_count):
        if tuple_count == 0:
            sub_exp_count = 1
        else:
            sub_exp_count = tuple_count

        for i in range(sub_exp_count):
            self._exp_path_dict[i] = ExpPaths(self,
                                              self.get_exp_name(i),
                                              create=True)

    def ensure_exp_paths(self, exp_count):
        if self.detect_exp_path(0):
            self.detect_exp_paths(count=exp_count)
        else:
            self.create_exp_paths(exp_count)

    def get_exp_count(self):
        if len(self._exp_path_dict) > 0:
            return max(self._exp_path_dict.keys()) + 1
        else:
            return 0

    def get_exp_paths(self, count):
        if count in self._exp_path_dict:
            return self._exp_path_dict[count]
        else:
            return None

    def get_exp_paths_by_name(self, name):
        for exp in self._exp_path_dict.values():
            if exp.exp_name == name:
                return exp
        return None

    def get_exp_paths_iterator(self):
        return self._exp_path_dict.values()

    @staticmethod
    def dir_hash(maybe_path):
        """
        Starting from a directory, gets all subdirectories, extracts the individual files and creates a hash value
        using the file name, size, and last modification date.

        Probably just modification date is enough.
        :param maybe_path:
        :return:
        """
        hasher = hashlib.sha1()
        path = force_path(maybe_path)
        full_listing = path.glob('**/*')
        files = [fl for fl in full_listing if fl.is_file()]
        for fl in files:
            fl_stat = fl.stat()
            fl_size = fl_stat.st_size
            fl_date = fl_stat.st_mtime
            fl_info = "{}-{}-{}".format(fl.name, fl_size, fl_date)
            fl_bytes = fl_info.encode('utf-8')
            hasher.update(fl_bytes)
        return hasher.hexdigest()


class ExpPaths:
    """
    Represents the various directories and paths associated with a single sub-experiment

    - log
    - result
    - original (for re-ranking)
    - conf
    """

    _LIBREC_PROPERTIES_FILE = 'librec.properties'
    DEFAULT_LOG_PATTERN = "librec-{}.log"

    _path_dict = None

    _prop_dict = {
        'log': 'dfs.log.dir',
        #                 'split': 'dfs.split.dir',
        'librec_result': 'dfs.result.dir',
        'conf': 'dfs.config.dir'
    }

    _sub_dirs = ['conf', 'log', 'result', 'original']

    exp_name = None

    def __init__(self, files, exp_name, create=True):
        self._path_dict = {}
        self.files = files
        base = files.get_study_path()
        self.exp_name = exp_name

        exp_path = base / exp_name
        self.set_path('subexp', exp_path)

        output_path = exp_path / 'output.xml'
        self.set_path('output', output_path)

        librec_result_path = Path(exp_name) / 'result'
        self.set_path('librec_result', librec_result_path)

        librec_prop_path = Path(
            exp_name
        ) / Files._DEFAULT_CONFIG_DIR_NAME / Files.DEFAULT_PROP_FILE_NAME
        self.set_path('librec_prop', librec_prop_path)

        for subdir in self._sub_dirs:
            subdir_path = exp_path / subdir
            self.set_path(subdir, subdir_path)

        if create:
            # if exp_path directory does not exist
            # create directory
            if not os.path.exists(exp_path):
                logging.info(f"Creating experiment: {exp_name}")
                exp_path.mkdir(exist_ok=True)
            for subdir in self._sub_dirs:
                self.get_path(subdir).mkdir(exist_ok=True)

    def get_path(self, type):
        if type in self._path_dict:
            return self._path_dict[type]
        else:
            return None

    def get_librec_properties_path(self):
        return self.get_path('librec_prop')
        # return self.get_path('conf') / Files.DEFAULT_PROP_FILE_NAME

    def get_ref_exp_flag_path(self):
        return self.get_path('conf') / Files.DEFAULT_REF_EXP_FILENAME

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

    def get_study_conf(self):
        path = self.get_path('conf') / Files.DEFAULT_CONFIG_FILENAME
        print("path files", path)
        xml_input = xml_load_from_path(path)
        return xml_input

    def get_ref_exp_name(self):
        ref_flag_file = self.get_ref_exp_flag_path()
        if ref_flag_file.exists():
            with ref_flag_file.open() as fh:
                exp_name = fh.readline()
                return exp_name.rstrip()
        else:
            return None

    def get_ref_exp_path(self):
        ref = self.get_ref_exp_name()
        if not ref:
            return None
        else:
            return self.files.get_exp_paths_by_name(ref)

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
        for file in files:
            os.remove(file)

    def get_log_path(self):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = ExpPaths.DEFAULT_LOG_PATTERN.format(stamp)
        return self.get_path('log') / fname

    def get_custom_metrics_log_path(self):
        return self.get_path('log') / 'python-metrics.json'
