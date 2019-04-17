import unittest
import config
import utils
import logging
import re
import collections


class TestConfigParse(unittest.TestCase):

    _XML1 = "<bad-xml>foo</bad>"
    _XML2 = '<?xml version="1.0"?>\
    <librec-auto>\
        <data id="filmtrust">\
            <data-path>../lib/librec/data/filmtrust/rating</data-path>\
            <data-format>text</data-format>\
            <data-column>UIR</data-column>\
        </data>\
    <exp id="test">\
        <data ref="filmtrust"/>\
        <splitter id="test"/>\
        <alg>itemknn-basic50</alg>\
    </exp>\
    </librec-auto>'
    _XML3 = '<?xml version="1.0"?>\
<librec-auto>\
    <data id="filmtrust">\
        <data-path>../lib/librec/data/filmtrust/rating</data-path>\
        <data-format>text</data-format>\
        <data-column>UIR</data-column>\
    </data>\
    <data ref="filmtrust">\
        <test>foo</test>\
    </data>\
    <data id="bad" ref="bad ref">\
        <test>foo</test>\
    </data>\
    <exp id="test">\
        <data ref="filmtrust"/>\
        <splitter id="test"/>\
        <alg>itemknn-basic50</alg>\
    </exp>\
</librec-auto>'
    _XML4 = '<?xml version="1.0"?>\
<librec-auto>\
    <data id="filmtrust">\
        <data-path>../lib/librec/data/filmtrust/rating</data-path>\
        <data-format>text</data-format>\
        <data-column>UIR</data-column>\
    </data>\
    <exp id="test">\
        <data ref="filmtrust"/>\
        <splitter id="test"/>\
        <alg>itemknn-basic50</alg>\
        <alg>userknn-basic50</alg>\
    </exp>\
</librec-auto>'
    _XML5 = '<?xml version="1.0"?>\
<librec-auto>\
    <data id="filmtrust">\
        <data-path>../lib/librec/data/filmtrust/rating</data-path>\
        <data-format>text</data-format>\
        <data-column>UIR</data-column>\
    </data>\
    <exp id="test">\
        <data ref="filmtrust"/>\
        <splitter id="test"/>\
        <alg name="test"> \
            <param name="test-param" from="1" to="5" by="1"/> \
            </alg>\
    </exp>\
</librec-auto>'

    def setUp(self):
        self.conf = config.Config("test/")
        logging.basicConfig(filename='log/example.log', level=logging.DEBUG)

    def test_malformed(self):
        self.conf.from_text(self._XML1)
        self.assertEqual(len(self.conf.to_dict()), 0, "Bad XML not handled")

    def test_element_create(self):
        self.conf.from_text(self._XML2)
        conf_dict = self.conf.to_dict()
        self.assertTrue('data' in conf_dict, "Data element not created.")
        self.assertTrue('filmtrust' in conf_dict['data'], "Data config not created")

    def test_ref_populate(self):
        self.conf.from_text(self._XML3)
        conf_dict = self.conf.to_dict()
        data_elems = conf_dict['data']
        eids = data_elems.keys()
        pat = re.compile("_UNNAMED\d+")
        unnamed = [eid for eid in eids if pat.match(eid)]
        self.assertTrue(len(unnamed) == 1, "Anonymous element not created")
        self.assertTrue('data-column' in conf_dict['data'][unnamed[0]], "Properties of referenced element not copied")

    def test_bad_ref(self):
        self.conf.from_text(self._XML3)
        conf_dict = self.conf.to_dict()
        self.assertTrue('bad' in conf_dict['data'], "Bad element not created")
        self.assertTrue('error' in conf_dict['data']['bad'], "Error element not created")

    def test_multi_alg(self):
        self.conf.from_text(self._XML4)
        exp_list = self.conf.get_experiment('test')
        self.assertEqual(len(exp_list), 2, "Multiple experiments not created for multiple algorithms")

    def test_iter_param(self):
        self.conf.from_text(self._XML5)
        exp_list = self.conf.get_experiment('test')
        self.assertEqual(len(exp_list), 5, "Multiple experiments not created for iteration parameters")

    def test_from_file(self):
        self.conf.from_file("conf/test-properties1.xml")
        loaded_config = self.conf.get_raw_configuration()
        self.assertTrue(type(loaded_config) is collections.OrderedDict,
                        "XML configuration file not loaded successfully.")
        self.assertTrue(len(loaded_config.values()) > 0, "XML configuration file not loaded successfully.")

    def test_inherit_param(self):
        self.conf.from_file("conf/test-properties1.xml")
        exp = self.conf.get_experiment('FT-IB-err')
        self.assertTrue('alg' in exp, "Missing alg element in experiment")
        self.assertTrue(utils.safe_xml_path(exp, ['alg', 'param']), "Missing parameters in experiment")
        self.assertTrue(any((param['@name'] == 'rec.similarity.class' for param in exp['alg']['param'])),
                        "Parameter not inherited for algorithm in experiment")

    def test_xform(self):
        self.conf.from_file("conf/test-properties1.xml")
        exp = self.conf.get_experiment('FT-IB-err')
        self.assertTrue('xform' in exp, "Missing xform element in experiment")
        self.assertTrue(utils.safe_xml_path(exp, ['xform', 'zero-action']), "Missing parameters in xform element")



if __name__ == '__main__':
    #
    # Leave this here, useful for running the debugger on specific tests
    # suite = unittest.TestSuite()
    # suite.addTest(TestConfigParse("test_inherit_param"))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)
    #
    unittest.main()
