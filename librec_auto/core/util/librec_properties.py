from collections import OrderedDict, defaultdict
from librec_auto.core.util import Files, utils, build_parent_path, xml_load_from_path, ExpPaths
from librec_auto.core.util.errors import UnknownConfigurationElementException
from lxml import etree
import copy
import logging
import itertools

# 2020-06-25 RB All new implementation

class LibrecTranslation:

    __instance = None

    fixed_param_dict = {
        'dfs.result.dir': 'result',
        'dfs.log.dir': 'log',
        'dfs.split.dir': 'split'
    }

    def __new__(cls, files):
        if LibrecTranslation.__instance is None:
            LibrecTranslation.__instance = object.__new__(cls)
            LibrecTranslation.files = files
        return LibrecTranslation.__instance

    def __init__(self, files):
        self.xml = self.read_rules(files)

    def read_rules(self, files):
        rules_path = self.files.get_rules_path()
        if (rules_path.exists()):
            rules_input = xml_load_from_path(rules_path)
            return rules_input
        else:
            logging.warning(f'No translation rules read from {rules_path}.')
            return None


class LibrecProperties:
    def __init__(self, xml, files):
        self.properties = LibrecTranslation.fixed_param_dict.copy()
        self._conf_xml = xml
        self.process_config(files)

    def process_config(self, files):
        trans_rules = LibrecTranslation(files)
        if type(self._conf_xml) is etree._Element:
            if type(trans_rules.xml) is etree._Element:
                self.process_aux(self._conf_xml, trans_rules.xml)
            else:
                logging.error("Element translations missing.")
        else:
            logging.error(f"Error processing experiment configuration file.")


# ctree: configuration tree
# rtree: rules tree
# recursively walk the ctree and the rtree at the same time
# if an element is labeled in the rules as "no-translate", that means it's contents are not passed to LibRec
#     and it can be ignored
#

    def process_aux(self, conf_tree: etree._Element,
                    rule_tree: etree._Element):
        for conf_elem in conf_tree.iterchildren(tag=etree.Element):
            conf_tag = conf_elem.tag
            rule_elem = rule_tree.findall(conf_tag)
            if len(rule_elem
                   ) > 0:  # If the entry corresponds to one or more rules
                if len(rule_elem) == 1:
                    rule_elem = rule_elem[0]
                    action_attr = rule_elem.get('action', default=None)
                    if action_attr is not None and action_attr == 'no-translate':  # If labeled "no translate", skip
                        pass
                    elif len(conf_elem
                             ) > 0:  # If the config file has subelements
                        if len(rule_elem
                               ) > 0:  # If the rules also have subelements
                            self.process_aux(conf_elem,
                                             rule_elem)  # recursive call
                        else:  # If no corresponding elements in rules
                            logging.warning(
                                f'Mismatch between element contents: {conf_elem} and rule: {rule_elem}'
                            )
                    else:  # Otherwise, it is a key-value pair
                        self.add_property(rule_elem.text, conf_elem.text)

                else:  # If the rules have a list,
                    self.process_multi(
                        conf_elem, rule_elem
                    )  # We are distinguishing cases based on attribute

            else:  # If the key isn't in the rules, ignore it but warn because it is probably an error.
  #              logging.warning(f"Tag {conf_tag} is not in element rules.")
                raise UnknownConfigurationElementException(conf_tag)


    # Two cases:
    # (a) We have multiple matching rules distinguished by attribute. For example,
    # 		<data-file>data.input.path</data-file>
    # 		<data-file format="*">data.model.format</data-file>
    #     In this case, the non-attribute version is handled in the normal way, but a second property is
    #     added, associating the associated attribute value with the key in that rule element.
    # (b) We have multiple matching rules not distinguished by attribute. For example,
    #       <l1-reg>rec.regularization.lambda1</l1-reg>
    #       <l1-reg>rec.slim.regularization.l1</l1-reg>
    #     In this case, we add all of the property mappings since unneeded ones are ignored by LibRec.
    #     The alternative would be to rename these for each algorithm, which is a lot for experimenters to have
    #     to remember.
    # The only difference between these cases is whether the rule element has an attribute or not.
    def process_multi(self, conf_elem, rule_elems):
        for rule_elem in rule_elems:
            key = rule_elem.text
            if rule_elem.attrib:
                attr = rule_elem.keys()[0]  # Case a
                val = conf_elem.get(attr)
            else:
                val = conf_elem.text
            self.add_property(key, val)

    # Multiple adds mean that the property is list-valued
    def add_property(self, key, val):
        if key in self.properties:
            old_val = utils.force_list(self.properties[key])
            old_val.append(val)
            self.properties[key] = old_val
        else:
            self.properties[key] = val

    def get_property(self, key):
        if key in self.properties:
            val = self.properties[key]
            if type(val) is list:
                return ','.join(val)
            else:
                return val
        else:
            return None

    def get_entries(self):
        return [(key, self.get_property(key))
                for key in self.properties.keys()]

    def save(self, exp: ExpPaths):
        path = exp.get_path('conf') / Files.DEFAULT_PROP_FILE_NAME
        with path.open('w') as fd:
            for (key, val) in self.get_entries():
                fd.write(f'{key}: {val}\n')
