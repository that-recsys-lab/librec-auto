from collections import OrderedDict

from . import xmltodict
import itertools
import logging
import string
from datetime import datetime
from .utils import force_list, safe_xml_path, frange
from pathlib2 import Path
import os

DEMO_PROPERTIES_DICT = \
    {
        "dfs.data.dir": "test/data",
        "dfs.result.dir": "result",
        "dfs.log.dir": "log",
        "data.input.path": "filmtrust.txt",
        "data.column.format": "UIR",
        "data.model.splitter": "kcv",
        "data.splitter.cv.number": "5",
        "data.splitter.ratio": "userfixed",
        "data.model.format": "text",
        "data.splitter.trainset.ratio": "0.8",
        "save.raw.data": "true",
        "rec.random.seed": "201701",
        "data.convert.binarize.threshold": "-1.0",
        "rec.eval.enable": "true",
        "rec.eval.classes": "rmse",
        "rec.recommender.isranking": "false",
        "rec.recommender.similarities": "item",
        "rec.similarity.class": "cos",
        "rec.neighbors.knn.number": "30",
        "rec.recommender.class": "net.librec.recommender.cf.ItemKNNRecommender"
    }


class ConfigSimple:
    _xml_input = None

    _rules_dict = None

    _prop_dict = None
    _var_data = None
    _post_script = None

    def __init__(self, path):

        self._xml_input = self.read_xml(path)

        self._rules_dict = self.read_rules(path)

        self._prop_dict = {}

        # the list is attached to 'rec.neighbors.knn.number'
        self._var_data = {}

    def get_prop_dict(self):
        return self._prop_dict

    def get_var_data(self):
        return self._var_data

    def get_post_script(self):
        return self._post_script

    def get_rules_dict(self):
        return self._rules_dict

    def read_rules(self, path_str):
        rule_path = Path(path_str) / "element-rules.xml"
        rules_input = self._load_from_file(rule_path)
        return rules_input

    def read_xml(self, path_str):
        path = Path(path_str) / "config.xml"
        xml_input = self._load_from_file(path)
        return xml_input

    def _load_from_file(self, path):
        """
        Loads the configuration file in a dictionary

        This is the raw configuration. Prints a warning and returns an empty dictionary
        if the file can't be read.
        :param path: The file name
        :return: A dictionary with the XML data
        """
        try:
            with path.open() as fd:
                txt = fd.read()
        except IOError as e:
            print ("Error reading ", path)
            print ("IO error({0}): {1}".format(e.errno, e.strerror))
            # logging.error("Error reading %s. IO error: (%d) %s", path, e.errno, e.strerror)
            return {}

        return self._load_from_text(txt)

    def _load_from_text(self, txt):
        try:
            conf_data = xmltodict.parse(txt)
        except xmltodict.expat.ExpatError as e:
            print ("Error parsing XML")
            print ("Expat error in line: {0}".format(e.lineno))
            # logging.error("Error parsing XML. Expat error in line %d", e.lineno)
            conf_data = {}

        return conf_data

    # A single python script is all we can handle
    def handle_post(self, script_tag):
        lang = script_tag['@lang']
        if lang == 'python2':
            self._post_script = script_tag['#text']
        else:
            logging.error("Only python2 scripts supported.")

    def translate(self):
        return self.translate_aux(self._xml_input['librec-auto'],
                                  self._rules_dict['librec-auto-element-rules'])

    def translate_aux(self, arg, rules):
        for key in arg:
            # Script tag is not handled by librec, doesn't become a property
            if key == 'script':
                self.handle_post(arg[key])
            elif type(arg[key]) is OrderedDict:           # If the config file has subelements
                if type(rules[key]) is OrderedDict:     # If the rules also have subelements
                    self.translate_aux(arg[key], rules[key]) # recursive call
                elif type(rules[key]) is list:          # If the rules have a list
                    self._prop_dict = self.translate_attr(arg[key], rules[key])  # We have an attribute
                elif 'value' in arg[key]:               # If the config file has a 'value' key
                    self._var_data[rules[key]] = arg[key]['value'] # then we have variable data
            elif key in rules: # Config file doesn't have subelements
                if type(arg[key]) is list:                    # Some properties have comma-separated values
                    self._prop_dict[rules[key]] = ','.join(arg[key])
                elif type(rules[key]) == list:   # There are multiple LibRec keys in which map to this LibRecAuto key. (e.g. 'l1-reg')
                    for libRecKey in rules[key]:
                        #print 'key ', libRecKey
                        #print 'k ', libRecKey
                        self._prop_dict[libRecKey] = arg[key]
                else:
                    self._prop_dict[rules[key]] = arg[key]  # Set property translation and value

        return

    def get_string_rule(self, attr_rule):
        for item in attr_rule:
            # if type(item) is unicode:
            if type(item) is str:
                    return item
        return None

    # Assumes attribute name is first in ordered dictionary.
    def collect_attributes(self, attr_rule):
        # return [(item.keys()[0], item['#text'])
        return [(list(item.keys())[0], item['#text'])
                for item in attr_rule if type(item) is OrderedDict]

    def translate_attr(self, elem, attr_rule):
        # Scan rule for string
        # Associate with elem #text
        string_rule = self.get_string_rule(attr_rule)
        if 'value' in elem:                             # Variable data
            self._var_data[string_rule] = elem['value']
        else:
            self._prop_dict[string_rule] = elem['#text']
        # Scan rule for all attributes
        # Assign
        attrib_pairs = self.collect_attributes(attr_rule)
        for attr_pair in attrib_pairs:
            self._prop_dict[attr_pair[1]] = elem[attr_pair[0]]
        return self._prop_dict

    # Need real implementation. Just a stub right now.
    def convert_properties(self):
        #if len(self._xml_input) == 0:
        #    # loading failed
        #    self._prop_dict = DEMO_PROPERTIES_DICT
        #    self._var_data = ("rec.neighbors.knn.number", [10, 20, 50, 100])
        #else:
            # convert
     #   self.xml_to_prop(self._xml_input)
        self.translate()


