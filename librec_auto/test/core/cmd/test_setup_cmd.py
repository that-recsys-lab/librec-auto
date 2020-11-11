from pathlib import Path
from shutil import rmtree

from librec_auto.core.cmd.setup_cmd import SetupCmd
from librec_auto.core import ConfigCmd


def _get_config():
    return ConfigCmd('librec_auto/test/test-config.xml', '')


def test_str():
    assert SetupCmd().__str__() == 'SetupCmd()'


def test_dry_run(capsys):
    captured = capsys.readouterr()  # capture stdout

    SetupCmd().dry_run(_get_config())

    exp_dir = Path('.') / Path('exp00000')
    _test_directory_structure(exp_dir)

    # check stdout
    out, err = capsys.readouterr()
    assert out == "librec-auto (DR): Executing setup command SetupCmd()\n"


def test_execute():
    SetupCmd().execute(_get_config())
    exp_dir = Path('.') / Path('exp00000')

    _test_directory_structure(exp_dir)


def test_setup():
    # currently does nothing, just passes
    SetupCmd().setup({})


def _test_directory_structure(exp):
    # test directory structure
    assert (exp).exists()
    assert (exp / Path('conf')).exists()
    assert (exp / Path('log')).exists()
    assert (exp / Path('original')).exists()
    assert (exp / Path('result')).exists()

    rmtree(exp)  # delete created directory
