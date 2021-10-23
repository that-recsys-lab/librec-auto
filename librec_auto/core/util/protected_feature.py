from lxml import etree
from collections import defaultdict
import logging
import copy
from pathlib import Path
import os



class ProtectedFeature:
    def __init__(self, protected_features: defaultdict, temp_dir) -> None:
        self._protected_features = protected_features
        self._temporary_file_directory = temp_dir
        self.create_protected_features_file()

    def cleanup(self):
        # cleanup temp directory
        pass

    def print_protected_features(self):
        for feature in self._protected_features:
            for var in self._protected_features[feature]:
                print(var, self._protected_features[feature][var])

    def get_protected_feature_names(self):
        return list(self._protected_features.keys())

    def protected_feature_cli(self, pro_feat=None):
        if pro_feat:
            # pro_feat will be a string/key to map to self._protected_features
            # which is a dict made of {attribute: value} pairs for a protected feature
            protected_feature = self._protected_features[pro_feat]
            cli_string = "--protected \"" + pro_feat
            for attr in protected_feature.keys():
                # if attr == 'xml':
                #     continue
                append_str = " " + attr + ":" + protected_feature[attr]
                cli_string = cli_string + append_str
            return cli_string + "\""
        else:
            master_string = ""
            for pf in self._protected_features.keys():
                if master_string == "":
                    cli_string = master_string + "--protected \"" + pf
                else:
                    cli_string = master_string + " --protected \"" + pf
                append_str = ""
                for attr in self._protected_features[pf].keys():
                    # if attr == 'xml':
                    #     continue
                    append_str = append_str + " " + attr + ":" + self._protected_features[pf][attr]
                master_string = cli_string + append_str + "\""
            return master_string
    
    def create_protected_features_file(self):
        temp_dir_path = self._temporary_file_directory
        protected_features_file = str(temp_dir_path / "protected-feature-file.xml")
        
        root = etree.Element("protected-feature-file")

        pf_copy = copy.deepcopy(self._protected_features)

        for protected_feature in pf_copy.keys():
            new_pf = etree.SubElement(root, 'protected_feature')
            new_pf.set('name', protected_feature)
            for attr in pf_copy[protected_feature].keys():
                if attr == 'column':
                    new_pf.text = pf_copy[protected_feature][attr]
                    continue
                new_pf.set(attr, pf_copy[protected_feature][attr])

        root.getroottree().write(protected_features_file, pretty_print=True)

        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(protected_features_file, parser)
        tree.write(protected_features_file, encoding='utf-8', pretty_print=True)
    
    def replace_referenced_protected_features(self, tree):
        # function for replacing the referenced protected features with all data
        root = tree
        ref_elements = root.findall('.//*[@ref]')
        
        for element in ref_elements:
            # only doing stuff with protected feature/parameter refs

            # if tag is 'protected-feature' then element not in script
            if element.tag == 'protected-feature':
                pf_name = element.attrib['ref']
                try:
                    protected_feat = copy.copy(self._protected_features[pf_name])
                    del element.attrib['ref']
                    element.attrib['type'] = protected_feat['type']
                    if 'values' in protected_feat.keys():
                        element.attrib['values'] = protected_feat['values']
                    element.text = protected_feat['column']
                except KeyError:
                    # should probably be changed to a LibrecException
                    logging.error(f"Referenced protected feature ({pf_name})\
                                  not in features section, or mismatched names.")
            # if tag is 'param' then element is in script
            elif element.tag == 'param':
                pf_name = element.attrib['ref']
                try:
                    protected_feat = copy.copy(self._protected_features[pf_name])

                    element.attrib['name'] = 'protected-feature'
                    del element.attrib['ref']
                    element.attrib['type'] = protected_feat['type']
                    if 'values' in protected_feat.keys():
                        element.attrib['values'] = protected_feat['values']
                    element.text = protected_feat['column']
                    
                        
                except KeyError:
                    # should probably be changed to a LibrecException
                    logging.error(f"Referenced protected feature ({pf_name})\
                                  not in features section, or mismatched names.")

        return root

    def lookup(self, feature_name):
        try:
            feat = copy.copy(self._protected_features[feature_name])
            return feat
        except KeyError:
            print(f"Feature {feature_name} not in dictionary")
            print(f"Available features: {self.get_protected_feature_names()}")
            

    @staticmethod
    def parse_protected(config):
        pf_dict = {}
        protected_features = config._xml_input.findall('features/protected-feature')
        for item in protected_features:
            if 'name' and 'type' not in item.keys():
                # raise InvalidConfiguration
                logging.error(f'Name and type are required attributes for protected feature.')    
            pf_name = item.attrib['name']
            pf_dict[pf_name] = {}
            for attr, val in item.items():
                if attr == 'name':
                    continue
                pf_dict[pf_name][attr] = val
            pf_dict[pf_name]['column'] = item.text
        return pf_dict

    