from collections import OrderedDict
from librec_auto.core.util import xmltodict, Files, utils, xml_load_from_path
import logging
import itertools
from pathlib import Path
from librec_auto.core.config_lib import ConfigLibCollection, ConfigLib


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
    _var_params = None
    _var_tuples = None
    _target = None
    _libraries = None

    IGNOREABLE_ATTRIBUTES = ['@ref', '@src', '@name']

    def __init__(self, config_file, target):

        self._files = Files()
        self._target = target

        # files.set_global_path(Path(__file__).parent.absolute())
        self._files.set_exp_path(target)
        self._files.set_config_file(config_file)

        self._xml_input = self.read_xml(self._files.get_config_path())

        self._rules_dict = self.read_rules()

        self._prop_dict = {}

        self._var_data = {}

        self._unparsed = {}

        self._var_params = []

        self._var_tuples = []

        self._libraries = ConfigLibCollection()

    def get_target(self):
        return self._target

    def get_prop_dict(self):
        return self._prop_dict

    def get_var_data(self):
        return self._var_data

    def get_value_tuple(self, subexp_no):
        return self._value_tuples[subexp_no]

    def get_sub_exp_count(self):
        exp_count = len(self._value_tuples)
        if exp_count == 0:
            return 1
        else:
            return exp_count

    # 2019-11-25 RB Configuration elements that aren't passed to LibRec are left in original XML format and handled
    # later in a command-specific way. A better way might be to have "handler" mechanism so that each command can
    # be associated its own configuration element and have code that is called when that element is encountered in the
    # parse. Something to think about.
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
            rules_input = xml_load_from_path(rules_path)
            return rules_input
        else:
            return None

    def read_xml(self, path_str):
        path = self._files.get_config_path()
        if (path.exists()):
            xml_input = xml_load_from_path(path)
            return xml_input
        else:
            return None

    def ensure_sub_experiments(self):
        exp_count = len(self._value_tuples)
        if exp_count == 0:
            exp_count = 1
        self.get_files().ensure_sub_paths(exp_count)

    def process_config(self):
        if type(self._xml_input) is OrderedDict:
            if type(self._rules_dict) is OrderedDict:
                self.setup_libraries()
                self.process_aux(self._xml_input['librec-auto'],
                                self._rules_dict['librec-auto-element-rules'])
                self.compute_value_tuples()
                self.ensure_sub_experiments()
            else:
                logging.error(f"Error processing element rules. Filename: {self._files.get_rules_path().as_posix()}")
        else:
            logging.error(f"Error processing configuration file. Filename: {self._files.get_config_path().as_posix()}")

    # Walk the configuration XML in tandem with the element rules to determine librec property translations for each
    # part of the configuration.
    def process_aux(self, arg, rules):
        for key in arg:
            if key in self.IGNOREABLE_ATTRIBUTES: # Skip bookkeeping attributes
                continue
            config_elem = self.augment_from_library(key, arg[key])
            if key in rules:                            # If the entry corresponds to a rule
                if "@action" in rules[key] and rules[key]['@action'] == 'no-parse': # If labeled "no parse" in rules
                    self._unparsed[key] = config_elem  # Add to unparsed collection
                elif type(config_elem) is OrderedDict:         # If the config file has subelements
                    if type(rules[key]) is OrderedDict:     # If the rules also have subelements
                        self.process_aux(config_elem, rules[key]) # recursive call
                    elif type(rules[key]) is list:          # If the rules have a list
                        self._prop_dict = self.process_attr(config_elem, rules[key])  # We have an attribute
                    elif 'value' in config_elem:               # If the config file has a 'value' key
                        self._var_data[rules[key]] = config_elem['value'] # then we have variable data for multiple exps.
                elif key in rules:                          # Config file doesn't have subelements
                    if type(config_elem) is list:              # Some properties have comma-separated values
                        self._prop_dict[rules[key]] = ','.join(config_elem)
                    elif type(rules[key]) == list:          # There are multiple LibRec keys in which map to this
                                                            # LibRecAuto key. (e.g. 'l1-reg')
                        for libRecKey in rules[key]:
                            if type(libRecKey) is str:            # Otherwise, it is a compound rule that doesn't match arg
                                self._prop_dict[libRecKey] = config_elem
                    else:
                        self._prop_dict[rules[key]] = config_elem  # Set property translation and value
            # If the key isn't in the rules, ignore it but warn because it is probably an error.
            else:
                logging.warning("Key {} is not in element rules.", key)

        return

    def augment_from_library(self, key, elem):
        if '@ref' not in elem:
            return elem
        else:
            ref = elem['@ref']
            lib_elem = self._libraries.get_element(ref).copy() # Don't want to overwrite library. Overly cautious?
            # Overwrite library entries with local
            if type(elem) is OrderedDict:
                for key,val in elem.items():
                    lib_elem[key] = val
            return lib_elem

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
        original_var_values = list(self._var_data.values())
        if (len(original_var_values) == 1):
            original_var_values = original_var_values[0]
        var_values = []
        for element in original_var_values:
            if type(element) is list:
                # print(element)
                var_values.append(element)
            else:
                var_values.append([element])
        if len(self.var_params) == 1:
            self._value_tuples = var_values
        else:
            self._value_tuples = list(itertools.product(*var_values))

    # TODO RB 2019-12-12 Should include some error-checking and better messages for badly-formed XML
    def collect_scripts(self, script_type):
        post_xml = self.get_unparsed(script_type)
        script_xml = post_xml['script']
        scripts = []
        for entry in utils.force_list(script_xml):
            script_path = utils.get_script_path(entry, script_type)
            if 'param' in entry:
                param_dict = {}
                for elem_dict in utils.force_list(entry['param']):
                    param_dict[elem_dict['@name']] = elem_dict['#text']
                scripts.append((script_path, param_dict))
            else:
                scripts.append((script_path, None))

        return scripts

    def setup_libraries(self):
        if utils.safe_xml_path(self._xml_input, ['librec-auto', 'library']):
            lib_elems = utils.force_list(utils.extract_from_path(self._xml_input, ['librec-auto', 'library']))
            for lib in lib_elems:
                lib_path = self.extract_library_path(lib)
                lib = ConfigLib(lib_path)
                self._libraries.append(lib)

    def extract_library_path(self, lib_elem):
        file_name = lib_elem['#text'] if type(lib_elem) is OrderedDict else lib_elem
        file_path = Path(file_name)
        path_prefix = None
        if type(lib_elem) is OrderedDict:
            if '@src' in lib_elem:
                if 'system' == lib_elem['@src']:
                    path_prefix = self._files.get_lib_path()
                else:
                    print(f'librec-auto: WARNING Path source {lib_elem["@src"]} is unknown. Possible values are: system')
        else: # If library path is just as string without directory information, assume conf directory
            if file_path.parent == Path('.'):
                path_prefix = self._files.get_config_path().parent
        if path_prefix is None:
            return file_path
        else:
            return path_prefix / file_path

def read_config_file(config_file, target):
    config = ConfigCmd(config_file, target)
    config.process_config()
    return config
