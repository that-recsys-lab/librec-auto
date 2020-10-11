import os
from pathlib import Path

import librec_auto
from librec_auto.core.cmd.install_cmd import InstallCmd
from librec_auto.core import ConfigCmd

def _get_config():
    return ConfigCmd('config.xml', '')

def test_str():
    install = InstallCmd()
    assert install.__str__() == 'InstallCmd()'

def test_dry_run(capsys):
    install = InstallCmd()
    captured = capsys.readouterr()
    print(captured.out)
    install.dry_run(_get_config())
    out, err = capsys.readouterr()
    assert out == "\nlibrec-auto (DR): Running install command InstallCmd()\n"

def test_execute():
    install_path = Path(librec_auto.__file__).parent
    jar_path = install_path / "jar" / "auto.jar"

    # remove jar if it already exists
    if os.path.exists(jar_path.absolute()):
        os.remove(jar_path.absolute())

    # set up the paths
    install_path = Path(librec_auto.__file__).parent
    jar_path = install_path / "jar" / "auto.jar"

    install = InstallCmd()
    install.execute(_get_config())

    # check if the jar exists
    assert jar_path.absolute().exists()
