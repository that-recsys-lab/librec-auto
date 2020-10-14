import os
import inspect
from sys import platform
from pathlib import Path

import librec_auto
from librec_auto.core.util import Files, ExpPaths


def test_init():
    files = Files()
    assert files.get_global_path() == Path(
        inspect.getfile(librec_auto)).parent.parent


def test_set_global_path():
    files = Files()
    test_path = Path('/demo/path/to/librec_auto')
    files.set_global_path(test_path)
    assert files.get_global_path() == test_path


def test_get_librec_paths():
    files = Files()
    test_path = Path('/demo/path/to/librec_auto')
    files.set_global_path(test_path)

    assert files.get_rules_path() == Path(
        '/demo/path/to/librec_auto/librec_auto/rules/element-rules.xml')

    assert files.get_lib_path() == Path(
        '/demo/path/to/librec_auto/librec_auto/library')

    assert files.get_jar_path() == Path(
        '/demo/path/to/librec_auto/librec_auto/jar')

    if platform == "win32":
        # for windows
        assert files.get_classpath(
        ) == 'D:/demo/path/to/librec_auto/librec_auto/jar/auto.jar', "Windows path is correct"
    else:
        assert files.get_classpath(
        ) == '/demo/path/to/librec_auto/librec_auto/jar/auto.jar', "Unix path is correct"


def test_get_study_paths():
    files = Files()
    files.set_study_path('demo99')

    assert files.get_study_path() == Path('demo99')

    assert files.get_config_dir_path() == Path('demo99/conf')

    assert files.get_post_path() == Path('demo99/post')
