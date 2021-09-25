from lxml import etree
from librec_auto.core.config_cmd import ConfigCmd
from collections import defaultdict
import logging
import copy

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

    @staticmethod
    def parse_protected(config: ConfigCmd):
        pf_dict = defaultdict(dict)
        protected_features = config._xml_input.findall('features/protected-feature')
        for item in protected_features:
            if 'name' and 'type' not in item.keys():
                # raise InvalidConfiguration
                logging.error(f'Name and type are required attributes for protected feature.')
            pf_name = item.attrib['name']
            for attr, val in item.items():
                if attr == 'name':
                    continue
                pf_dict[pf_name][attr] = val
            pf_dict[pf_name]['column'] = item.text
            # pf_dict[pf_name]['xml'] = item
            
            
        # for key in pf_dict.keys():
        #     print(key, pf_dict[key].items(), list(pf_dict[key]))
        return pf_dict

if __name__ == '__main__':
    target = '/Users/will/Desktop/work/librec-auto-demo2020/demo02'
    conf_file = os.getcwd() + '/librec_auto/core/config2.xml'
    test_config = ConfigCmd(conf_file, target)
    temp_dir = test_config._files.get_temp_dir_path()
    # print(test._protected_features)
    # print(test.protected_feature_cli('ed_rank'))
    # print(test.protected_feature_cli())
    tester = ProtectedFeature(ProtectedFeature.parse_protected(test_config), temp_dir=temp_dir)
    print(tester.get_protected_feature_names())
    print(tester.protected_feature_cli())
    





# if element.tag == 'protected-feature' or element.tag == 'param':
#     pf_name = element.attrib['ref']
#     try:
#         protected_feat = copy.copy(self._protected_features[pf_name])
#         # element = protected_feat['xml']
#         element.attrib['name'] = 'protected'
#         del element.attrib['ref']

#         for attr in protected_feat.keys():
#             if attr == 'column':
#                 continue                       
#             element.attrib[attr] = protected_feat[attr]
        
#         element.text = protected_feat['column']
        
            
#     except KeyError:
#         # should probably be changed to a LibrecException
#         logging.error(f"Referenced protected feature ({attr}) not in features section, or mismatched names.")

# def get_protected_features(self):
#         pf_dict = defaultdict(dict)
#         print(type(pf_dict))
#         protected_features = self._xml_input.findall('features/protected-feature')
#         for item in protected_features:
#             if 'name' and 'type' not in item.keys():
#                 # raise InvalidConfiguration
#                 logging.error(f'Name and type are required attributes for protected feature.')
#             pf_name = item.attrib['name']
#             for attr, val in item.items():
#                 if attr == 'name':
#                     continue
#                 pf_dict[pf_name][attr] = val
#             pf_dict[pf_name]['column'] = item.text
#             # pf_dict[pf_name]['xml'] = item
            
            
#         # for key in pf_dict.keys():
#         #     print(key, pf_dict[key].items(), list(pf_dict[key]))
#         return pf_dict

# def protected_feature_cli(self, pro_feat=None):
#     if pro_feat:
#         # pro_feat will be a string/key to map to self._protected_features
#         # which is a dict made of {attribute: value} pairs for a protected feature
#         protected_feature = self._protected_features[pro_feat]
#         cli_string = "--protected \"" + pro_feat
#         for attr in protected_feature.keys():
#             # if attr == 'xml':
#             #     continue
#             append_str = " " + attr + ":" + protected_feature[attr]
#             cli_string = cli_string + append_str
#         return cli_string + "\""
#     else:
#         master_string = ""
#         for pf in self._protected_features.keys():
#             if master_string == "":
#                 cli_string = master_string + "--protected \"" + pf
#             else:
#                 cli_string = master_string + " --protected \"" + pf
#             append_str = ""
#             for attr in self._protected_features[pf].keys():
#                 # if attr == 'xml':
#                 #     continue
#                 append_str = append_str + " " + attr + ":" + self._protected_features[pf][attr]
#             master_string = cli_string + append_str + "\""
#         return master_string


# def replace_referenced_protected_features(self, new_xml):
#     # find the protected freatures that are referenced in the config file
#     # if filepath:
#     #     xml_file = str(filepath)
#     # else:    
#     #     xml_file = str(self._files.get_config_file_path())
#     tree = etree.parse(new_xml)
#     root = tree.getroot()
#     ref_elements = root.findall('.//*[@ref]')
    
#     for element in ref_elements:
#         if element.tag == 'protected-feature' or element.tag == 'param':
#             pf_name = element.attrib['ref']
#             try:
#                 protected_feat = copy.copy(self._protected_features[pf_name])
#                 # element = protected_feat['xml']
#                 element.attrib['name'] = 'protected'
#                 del element.attrib['ref']

#                 for attr in protected_feat.keys():
#                     if attr == 'column':
#                         continue                       
#                     element.attrib[attr] = protected_feat[attr]
                
#                 element.text = protected_feat['column']
                
                    
#             except KeyError:
#                 # should probably be changed to a LibrecException
#                 logging.error(f"Referenced protected feature ({attr}) not in features section, or mismatched names.")

#     return tree
#     # tree.write(file_path, pretty_print=True)

#     # parser = etree.XMLParser(remove_blank_text=True)
#     # tree = etree.parse(file_path, parser)
#     # tree.write(file_path, encoding='utf-8', pretty_print=True)

# def make_protected_params(elems: list) -> etree._Element:
#     return 0