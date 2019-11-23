from collections import OrderedDict
from librec_auto.util import xmltodict
import logging
import itertools


class ConfigCmd:
    """
    Loads the configuration file using the element rules. Elements labels as "unparsed" in the rules are added to the
    _unparsed collection later processing.

    """

    _xml_input = None
    _rules_dict = None
    _prop_dict = None
    _var_data = None
    _unparsed = None
    var_params = None
    _var_tuples = None

    def __init__(self, files):

        self._files = files

        self._xml_input = self.read_xml(files.get_config_path())

        self._rules_dict = self.read_rules()

        self._prop_dict = {}

        self._var_data = {}

        self._unparsed = {}

        self._var_params = []

        self._var_tuples = []

    def get_prop_dict(self):
        return self._prop_dict

    def get_var_data(self):
        return self._var_data

    def get_value_tuple(self, subexp_no):
        return self._value_tuples[subexp_no]

    def get_unparsed(self, type):
        if type in self._unparsed:
            return self._unparsed[type]
        else:
            None

    def get_rules_dict(self):
        return self._rules_dict

    def get_files(self):
        return self._files

    def read_rules(self):
        rules_path = self._files.get_rules_path()
        if (rules_path.exists()):
            rules_input = self._load_from_file(rules_path)
            return rules_input
        else:
            return None

    def read_xml(self, path_str):
        path = self._files.get_config_path()
        if (path.exists()):
            xml_input = self._load_from_file(path)
            return xml_input
        else:
            return None

    def _load_from_file(self, path):
        """
        Loads the configuration file in a dictionary

        This is the raw configuration. Prints a warning and returns an empty dictionary
        if the file can't be read.
        :param path: The file name
        :return: A dictionary with the XML rules
        """
        try:
            with path.open() as fd:
                txt = fd.read()
        except IOError as e:
            print ("Error reading ", path)
            print ("IO error({0}): {1}".format(e.errno, e.strerror))
            logging.error("Error reading %s. IO error: (%d) %s", path, e.errno, e.strerror)
            return None

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

    def process_config(self):
        if type(self._xml_input) is OrderedDict:
            if type(self._rules_dict) is OrderedDict:
                self.process_aux(self._xml_input['librec-auto'],
                                self._rules_dict['librec-auto-element-rules'])
                self.compute_value_tuples()
                self.get_files().create_sub_paths(len(self._value_tuples))
            else:
                logging.error("Error processing element rules. Filename: {}", self._files.get_rules_path())
        else:
            logging.error("Error processing configuration file. Filename: {}", self._files.get_config_path())

    def process_aux(self, arg, rules):
        for key in arg:
            if key in rules:                                # If the entry corresponds to a rule
                if "@action" in rules[key] and rules[key]['@action'] == 'no-parse': # If labeled "no parse"
                    self._unparsed[key] = arg[key]          # Add to unparsed collection
                elif type(arg[key]) is OrderedDict:         # If the config file has subelements
                    if type(rules[key]) is OrderedDict:     # If the rules also have subelements
                        self.process_aux(arg[key], rules[key]) # recursive call
                    elif type(rules[key]) is list:          # If the rules have a list
                        self._prop_dict = self.process_attr(arg[key], rules[key])  # We have an attribute
                    elif 'value' in arg[key]:               # If the config file has a 'value' key
                        self._var_data[rules[key]] = arg[key]['value'] # then we have variable data for multiple exps.
                elif key in rules:                          # Config file doesn't have subelements
                    if type(arg[key]) is list:              # Some properties have comma-separated values
                        self._prop_dict[rules[key]] = ','.join(arg[key])
                    elif type(rules[key]) == list:          # There are multiple LibRec keys in which map to this
                                                            # LibRecAuto key. (e.g. 'l1-reg')
                        for libRecKey in rules[key]:
                            self._prop_dict[libRecKey] = arg[key]
                    else:
                        self._prop_dict[rules[key]] = arg[key]  # Set property translation and value
            # If the key isn't in the rules, ignore it but warn because it is probably an error.
            else:
                logging.warning("Key {} is not in element rules.", key)

        return

    def get_string_rule(self, attr_rule):
        for item in attr_rule:
            if type(item) is str:
                    return item
        return None

    # Assumes attribute name is first in ordered dictionary.
    def collect_attributes(self, attr_rule):
        return [(list(item.keys())[0], item['#text'])
                for item in attr_rule if type(item) is OrderedDict]

    def process_attr(self, elem, attr_rule):
        # Scan rule for string
        # Associate with elem #text
        string_rule = self.get_string_rule(attr_rule)
        if 'value' in elem:                             # Variable rules
            self._var_data[string_rule] = elem['value']
        else:
            self._prop_dict[string_rule] = elem['#text']
        # Scan rule for all attributes
        # Assign
        attrib_pairs = self.collect_attributes(attr_rule)
        for attr_pair in attrib_pairs:
            self._prop_dict[attr_pair[1]] = elem[attr_pair[0]]
        return self._prop_dict

    def compute_value_tuples(self):
        self.var_params = self._var_data.keys()
        original_var_values = self._var_data.values()
        var_values = []
        for element in original_var_values:
            if type(element) is list:
                # print(element)
                var_values.append(element)
            else:
                var_values.append([element])
        if len(var_values) == 1:
            self._value_tuples = [var_values]
        else:
            self._value_tuples = list(itertools.product(*var_values))


