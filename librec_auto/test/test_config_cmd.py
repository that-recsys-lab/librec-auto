import unittest
from librec_auto.config_cmd import ConfigCmd
from librec_auto.util.files import Files
from collections import OrderedDict
from pathlib import Path


class ConfigCmdTestCase(unittest.TestCase):
    def setUp(self):
        self.files = Files()
        self.files.set_study_path('.')
        self.files.set_config_file('config-test.xml')
        self.files.set_global_path('..')

    def test_exists(self):
        config_path = Path('conf/config-test.xml')
        self.assertTrue(config_path.exists())

    def test_loadRules(self):
        config = ConfigCmd(self.files)
        self.assertIsInstance(config.get_rules_dict(), OrderedDict)

    def test_loadConfig(self):
        config = ConfigCmd(self.files)
        self.assertIsInstance(config._xml_input, OrderedDict)

    def test_processConfig(self):
        config = ConfigCmd(self.files)
        config.process_config()
        self.assertTrue(len(config.get_prop_dict()) > 0)
        self.assertEqual(config.get_prop_dict()['rec.recommender.class'],
                         'biasedmf')

    def test_processUnparsed(self):
        config = ConfigCmd(self.files)
        config.process_config()
        self.assertIsInstance(config.get_unparsed('rerank'), OrderedDict)
        self.assertTrue('script' in config.get_unparsed('rerank'))


if __name__ == '__main__':
    unittest.main()
