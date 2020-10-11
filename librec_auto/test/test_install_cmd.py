import unittest
import os
from pathlib import Path

import librec_auto
from librec_auto.core.cmd.install_cmd import InstallCmd
from librec_auto.core import ConfigCmd

class TestInstallCmd(unittest.TestCase):
    def setUp(self):
        install_path = Path(librec_auto.__file__).parent
        jar_path = install_path / "jar" / "auto.jar"

        # remove jar if it already exists
        if os.path.exists(jar_path.absolute()):
            os.remove(jar_path.absolute())

    def test_execute(self):
        # set up the paths
        install_path = Path(librec_auto.__file__).parent
        jar_path = install_path / "jar" / "auto.jar"

        # set up the config
        config = ConfigCmd('config.xml', "")

        install = InstallCmd()
        install.execute(config)

        # check if the jar exists
        self.assertTrue(jar_path.absolute().exists())
