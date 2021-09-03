import os
import re
import subprocess
import copy
from collections import defaultdict
from librec_auto.core.cmd import Cmd
from librec_auto.core.config_cmd import ConfigCmd
from librec_auto.core.util import LogFile
from librec_auto.core.util.xml_utils import single_xpath, xml_load_from_path
from librec_auto.core.util.errors import *
from pathlib import Path
from lxml import etree

# What Check is designed to check for:
# 1. paths are legal (include paths to scripts). Include both "system" and user-defined
# 2. we have write permission to files and directories
# 3. no necessary element are missing: data, splitter, alg, metric
# 4. if optimize, must be upper/lower elements in alg. Must NOT be value elements
# 5. if library reference, the ref exists.
# 6. (eventually) XML validation against schema
# 7. (eventually) validate script parameters. scripts must conform.
# 8. (eventually) fix Java side so that check command doesn't load data files and only runs once.

def check_output_xml(filepath):
    if os.path.exists(filepath):
        doc = xml_load_from_path(Path(filepath))
        num_elements = len(doc.getchildren())
        return num_elements
    return 0

class CheckCmd(Cmd):
    """
    Checks the configuration file to make sure everything necessary is there,
    possibly giving reminders of the full extent/capabilities of LibRec-Auto
    if the user misses certain elements.
    """

    def __str__(self):
        return f"CheckCmd()"

    def setup(self, args):
        pass

    def dry_run(self, config):
        print(f'librec-auto (DR): Running check command {self}')
    
    def execute(self, config: ConfigCmd):
        self._status = Cmd.STATUS_INPROC
        files = config.get_files()
        pwd = files.get_study_path()
        config_xml = config._xml_input
        config_elements = config_xml.getchildren()

        output_path = config.get_files().get_study_path()
        output_xml_path = str(output_path / "output.xml")
        study_ran = Path(output_xml_path).exists()
        check_output_xml(output_xml_path)
        if study_ran:
            os.remove(output_xml_path)

        # check should  be the first thing writing to an output.xml file
        output_tree = etree.Element("study")
        # clear the check elements from before, if present
        check_element = output_tree.find('check')
        if check_element is not None:
            output_tree.remove(check_element)
    
        # check all paths have write access.
        for func in dir(files):
            if re.match(r'get_.*path$', func):
                getpath = getattr(files, func)
                if func == 'get_status_path' or func == 'get_post_path':
                    continue
                if not os.access(getpath(), os.W_OK):
                    raise InvalidConfiguration(getpath(), f"Write access not granted {func}")
            
        # check all necessary elements are in config
        curr_elem = [e.tag for e in config_elements]
        necc_elem = {'data': 'Data section',
                     'splitter': 'Splitter section', 
                     'alg': 'Algorithm section',
                     'metric': 'Metric section'}
        for elem in necc_elem.keys():
            if elem not in curr_elem:
                raise InvalidConfiguration(necc_elem[elem], f"{necc_elem[elem]} missing in configuration file.")

        
        # checking library
        library = single_xpath(config_xml, '/librec-auto/library')
        if library.attrib['src'] == "system":
            lib_path = files.get_lib_path() / library.text
        else:
            lib_path = pwd / library.attrib['src'] / library.text
        if not lib_path.exists():
            raise InvalidConfiguration(lib_path, "Library not found at give path.")
        
        # Checking data.
        data_dir = single_xpath(config_xml, '/librec-auto/data/data-dir')
        # Test to see how many data directories were given.
        num_data_dir_test = config_xml.xpath('/librec-auto/data/data-dir')
        if len(num_data_dir_test) > 1:
            raise InvalidConfiguration("Data Directory", "More than one data file found.")
        # Checking path to data directory
        data_dir_path = Path(pwd / data_dir.text)
        data_file = single_xpath(config_xml, '/librec-auto/data/data-file')
        data_file_path = Path(data_dir_path / data_file.text)
        if not data_file_path.exists():
            raise InvalidConfiguration(str(data_file_path), "Data file not found at given path.")
        

        # checking script paths/files exist and that scripts are in approved locations
        for elem in config_elements:
            script_element = elem.findall('script')
            # findall returns list, check for items.
            if script_element:
                # Iterate over scripts.
                for se in script_element:
                    if se.attrib['src'] == "system":
                        if elem.tag == 'metric':
                            script_path = files.get_global_path() / 'librec_auto' / 'core' / 'cmd' / 'eval'
                        elif elem.tag == 'post':
                            script_path = files.get_global_path() / 'librec_auto' / 'core' / 'cmd' / 'post'
                        elif elem.tag == 'rerank':
                            script_path = files.get_global_path() / 'librec_auto' / 'core' / 'cmd' / 'rerank'
                        else:
                            raise InvalidConfiguration(elem.tag, f"Scripts not allowed in {elem.tag} section.")
                    else:
                        script_path = Path(se.attrib['src'])
                    script_name = se.find('script-name')
                    script_path = script_path / script_name.text
                    if not script_path.exists():
                        raise InvalidConfiguration(str(script_path), f'{script_name.text} not found in given path.')
            # else: if there aren't script elements do nothing, for now

        if 'optimize' in curr_elem:
            alg = single_xpath(config_xml, '/librec-auto/alg')
            if alg is not None:
                for elem in alg:
                    # parameters being optimized should have children, upper and lower
                    if elem.getchildren():
                        children = [e.tag for e in elem.iterchildren()]
                        if 'value' in children: # impossible case: librec-auto setup catches this first. 
                            raise InvalidConfiguration('Optimization', 'Value tags not allowed in optimize element')
                        else:
                            if 'lower' and 'upper' not in children:
                                raise InvalidConfiguration('Optimization', f'Lower and upper tags missing in {elem.tag}')
                    else:
                        # for now continue, should add check to make sure value
                        # from reference xml and config xml are same type.
                        continue
                

        # create filepath attribute for errors as src
        # if the compiler makes it to here without raising an error, then there are no errors
        if not study_ran: # if the output file doesn't exist
            check_tree = etree.SubElement(output_tree, "check")
            message_element = etree.SubElement(check_tree, "message")
            message_element.text = "No errors found in configuration file syntax."
        else: # if it does
            check_tree = etree.Element("check")
            message_element = etree.SubElement(check_tree, "message")
            message_element.text = "No errors found in configuration file syntax."
            output_tree.insert(2, check_tree)

        # reading the Java logs
        # check command shouldn't care about librec.properties file not found (unless run was ran)
        for i in range(0, config.get_sub_exp_count()):
            exp_path = config.get_files().get_exp_paths(i)
            log_object = LogFile(exp_path, study_ran)
            # src: filepath
            check_tree = output_tree.find('check')
            if check_tree is not None:
                if len(log_object._err_msgs.keys()) != 0:
                    # dict-list comprehension to filter out ignorable errors
                    temp_dict = {k:[m for _, m in log_object._err_msgs[k] if not self.is_ignorable_error(m)]
                                                                    for k in log_object._err_msgs.keys()}
                    # filter out empty lists
                    temp_dict = {k:v for k,v in temp_dict.items() if v}
                    # iterate over filtered dictionary                    
                    if len(temp_dict.keys()) != 0:
                        for error in temp_dict.keys():
                            for line_number, message in temp_dict[error]:
                                message_element = etree.SubElement(check_tree, "message", {'src': str(exp_path), 
                                                                                           'logline': str(line_number),
                                                                                           'exp_num': str(i)})
                                message_element.text = message.strip('\n')
                    else:
                        message_element = etree.SubElement(check_tree, "message", {'src': str(log_object._log_path)})
                        message_element.text = f"No errors found in experiment {i} log."
                else:
                    message_element = etree.SubElement(check_tree, "message", {'src': str(log_object._log_path)})
                    message_element.text = f"No errors found in experiment {i} log."

        output_tree.getroottree().write(output_xml_path, pretty_print=True)

        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(output_xml_path, parser)
        tree.write(output_xml_path, encoding='utf-8', pretty_print=True)

        self._status = Cmd.STATUS_COMPLETE


    def is_ignorable_error(self, message):
        '''
        This function can be updated with any other errors deemed 'ignorable' by 
        creating a regex string and elif block.
        '''
        property_file_error_pattern = r'.*java\.io\.FileNotFoundException: exp\d*/conf/librec\.properties.*'
        if re.match(property_file_error_pattern, message):
            return True
        return False
    
        

