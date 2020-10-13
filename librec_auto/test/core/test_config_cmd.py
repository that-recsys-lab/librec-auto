import os
from pathlib import Path
import shutil
from collections import defaultdict

from librec_auto.core import ConfigCmd, read_config_file


def _get_config():
    return ConfigCmd('config.xml', '')


def test_read_config_cmd():
    # this file does not exist
    invalid_config = read_config_file('config.xml', '')
    # ...so the config is invalid
    assert invalid_config.is_valid() == False

    # this file exists
    invalid_config = read_config_file('config.xml', 'librec_auto/test/temp')
    # so the config is valid
    assert invalid_config.is_valid() == True
    # and the ._var_data attribute has been initialized
    assert invalid_config._var_data == defaultdict(list)
