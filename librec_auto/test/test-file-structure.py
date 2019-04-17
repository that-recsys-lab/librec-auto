import unittest
import files
import logging


class TestFileStructure(unittest.TestCase):

    GLOBAL_PATH = 'test-files/global_home/'
    USER_PATH = 'test-files/user_home/'
    EXP_PATH = 'test-files/exp_home/'

    def setUp(self):
        self.files = files.Files()
        self.files.set_global_path(self.GLOBAL_PATH)
        self.files.set_user_path(self.USER_PATH)
        self.files.set_exp_path(self.EXP_PATH)

        logging.basicConfig(filename='log/example.log', level=logging.DEBUG)

    def test_file_search(self):
        p1 = self.files.find_config_file('test-include1.xml')
        self.assertNotEqual(p1, None, 'Global config file not found.')
        p2 = self.files.find_config_file('test-include2.xml')
        self.assertNotEqual(p2, None, 'User config file not found.')
        p3 = self.files.find_config_file('test-properties.xml')
        self.assertNotEqual(p3, None, 'Experiment config file not found.')

    def test_dir_update(self):
        hash1 = self.files.dir_hash(self.files.get_exp_path())
        canary_path = self.files.find_config_file('canary.txt')
        canary_path.touch()
        hash2 = self.files.dir_hash(self.files.get_exp_path())
        self.assertNotEqual(hash1, hash2, "Directory hash unchanged with new mod date.")


if __name__ == '__main__':
    # Leave this here, useful for running the debugger on specific tests
    # foo = TestFileStructure("test")
    # suite = unittest.TestSuite()
    # suite.addTest(TestFileStructure("test_file_search"))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)
    unittest.main()
