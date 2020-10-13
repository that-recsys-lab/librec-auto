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

    # make temp directory
    Path('librec_auto/test/temp').mkdir(exist_ok=True)
    Path('librec_auto/test/temp/conf').mkdir(exist_ok=True)

    # copy the config into the temp directory
    current_config = Path('librec_auto/test/test-config.xml')
    new_config = Path('librec_auto/test/temp/conf/test-config.xml')
    shutil.copy(current_config, new_config)

    # this file exists
    invalid_config = read_config_file('test-config.xml',
                                      'librec_auto/test/temp')

    # so the config is valid
    assert invalid_config.is_valid() == True

    # and the ._var_data attribute has been initialized
    assert invalid_config._var_data == defaultdict(list)

    # break down the temp dir
    shutil.rmtree(Path('librec_auto/test/temp'))
