import shutil
import time
from os import scandir, name
from pathlib import Path

import librec_auto.__main__ as main
from librec_auto.core.cmd.purge_cmd import PurgeCmd
from librec_auto.core import ConfigCmd

POST_DIR = 'librec_auto/test/core/cmd/post'

STUDY_DIR = 'librec_auto/test/core/cmd/study'


def _get_config():
    config = ConfigCmd('librec_auto/test/test-config.xml', '')
    config._files.set_post_path(POST_DIR)
    return config


def test_purge_type():
    assert main.purge_type({'purge': 'all'}) == 'all'

    assert main.purge_type({'action': 'purge'}) == 'split'

    assert main.purge_type({'action': 'notpurge'}) == 'none'


def test_str():
    assert PurgeCmd(_get_config()).__str__().startswith("PurgeCmd(")


def test_setup():
    # no checks, just pass in the implementation
    PurgeCmd(_get_config).setup({})


def test_dry_run(capsys):
    captured = capsys.readouterr()  # capture stdout

    PurgeCmd(_get_config).dry_run(_get_config())

    out, err = capsys.readouterr()
    assert out.startswith(
        "librec-auto (DR): Executing purge command PurgeCmd(")


def test_purge_post(capsys):
    # test case where directory is missing
    purge = PurgeCmd(_get_config())
    purge._files = _get_config().get_files()

    captured = capsys.readouterr()  # capture stdout

    purge.purge_post()

    out, err = capsys.readouterr()
    assert out == "librec-auto: Post directory missing .\n"

    # test case where directory exists

    # make the directory
    test_dir = Path(POST_DIR)
    test_dir.mkdir(exist_ok=True)

    # add test files
    (test_dir / Path('post1.xml')).touch()
    (test_dir / Path('post2.xml')).touch()

    purge.purge_post()  # purge

    # check test files are removed
    assert list(test_dir.glob('*')) == []

    # delete the directory
    shutil.rmtree(test_dir)


def test_purge_subexperiments(capsys):
    # create purge command
    purge = PurgeCmd(_get_config())

    # create study dir
    Path(STUDY_DIR).mkdir(exist_ok=True)

    # set study path
    purge._files = _get_config().get_files()
    purge._files.set_study_path(STUDY_DIR)

    # case: no subexperiments in the directory

    captured = capsys.readouterr()  # capture stdout

    purge.purge_subexperiments()

    out, err = capsys.readouterr()
    if name == 'nt':
        # running on Windows
        assert out == """librec-auto: Purging sub-experiments librec_auto\\test\\core\\cmd\\study
librec-auto: No experiments folders found in librec_auto\\test\\core\\cmd\\study
"""
    else:
        # non-Windows
        assert out == """librec-auto: Purging sub-experiments librec_auto/test/core/cmd/study
librec-auto: No experiments folders found in librec_auto/test/core/cmd/study
"""

    # case: three subexperiments in the directory

    # create three experiment subdirs
    purge._files.ensure_exp_paths(3)
    assert len([f.path for f in scandir(STUDY_DIR) if f.is_dir()]) == 3

    # purge subexperiments
    purge.purge_subexperiments()

    # confirm no subexperiments in dir
    assert len([f.path for f in scandir(STUDY_DIR) if f.is_dir()]) == 0

    # delete test directory
    shutil.rmtree(Path(STUDY_DIR))


def test_purge_rerank(capsys):
    pass
    # todo


def test_execute():
    config = _get_config()
    purge = PurgeCmd(_get_config())
    purge._no_ask = True

    purge._type = "all"
    purge.execute(config)

    purge._type = "results"
    purge.execute(config)

    purge._type = "rerank"
    purge.execute(config)

    purge._type = "post"
    purge.execute(config)
