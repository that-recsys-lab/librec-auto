import os
import re
import subprocess
import copy
from collections import defaultdict
from librec_auto.core.cmd import Cmd
from librec_auto.core.config_cmd import ConfigCmd
from librec_auto.core.util import LogFile
from librec_auto.core.util.xml_utils import single_xpath
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
# 8. (eventually) fix Java side so that check command doesn't load and only runs once.

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
        print(f'librec-auto (DR): Running status command {self}')
    
    def execute(self, config: ConfigCmd):
        self._status = Cmd.STATUS_INPROC
        files = config.get_files()
        pwd = files.get_study_path()
        config_xml = config._xml_input
        config_elements = config_xml.getchildren()

        output_path = config.get_files().get_study_path()
        output_xml_path = str(output_path / "output.xml")
        study_ran = Path(config.get_files().get_status_path()).exists()

        if study_ran:
            # Experimenter wants to run `check` after `run`, so output_xml should exist
            output_tree = etree.parse(output_xml_path).getroot()
        else:
            # Study has not been run, will need to create output.xml
            output_tree = etree.Element("study")

        errors = defaultdict(list)

        # build check to make sure Java version is correct/installed (any version) >1.8 is ideal
        # so many kinds of Java, may want separate function to do this
        java_version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT) # returns bytestring
        java_version = java_version.decode("utf-8") # convert to regular string
        version_pattern = r'\"(\d+\.\d+).*\"' # regex pattern matching
        version = re.search(version_pattern, java_version).groups()[0] 
        # print(f'Java version number: {version}')
        # print(java_version)

        # create new metric that breaks, see where error goes

        # potentially make new class of exceptions to catch our errors
        # create errors.py in util
    
        # check all paths have write access.
        for func in dir(files):
            if re.match(r'get_.*path$', func):
                getpath = getattr(files, func)
                if func == 'get_status_path':
                    if study_ran:
                        if not os.access(getpath(), os.W_OK):
                            errors['access'].append(f'***** Write access not granted'
                                                    f' for {getpath()}. *****')
                    else:
                        continue
                if not os.access(getpath(), os.W_OK):
                    errors['access'].append(f'***** Write access not granted '
                                            f'for {getpath()}. *****')
            
        # check all necessary elements are in config
        curr_elem = [e.tag for e in config_elements]
        necc_elem = {'data': 'Data section',
                     'splitter': 'Splitter section', 
                     'alg': 'Algorithm section',
                     'metric': 'Metric section'}
        for elem in necc_elem.keys():
            if elem not in curr_elem:
                errors['element'].append(f'***** {necc_elem[elem]} missing in '
                                          f'config file. *****')
        
        # checking library
        library = single_xpath(config_xml, '/librec-auto/library')
        if library.attrib['src'] == "system":
            lib_path = Path(files.get_lib_path() / library.text)
        else:
            lib_path = Path(pwd) / library.attrib['src'] / library.text
        if not lib_path.exists():
            errors['library'].append(f'***** Library not found. Given path: {lib_path} *****')
        
        # checking data
        data_dir = single_xpath(config_xml, '/librec-auto/data/data-dir')
        test = config_xml.xpath('/librec-auto/data/data-dir')
        if len(test) > 1:
            errors['data'].append(f'***** More than one data file found. Using: {data_dir.text} *****')
        data_dir_path = Path(pwd / data_dir.text)
        data_file = single_xpath(config_xml, '/librec-auto/data/data-file')
        data_file_path = Path(data_dir_path / data_file.text)
        if not data_file_path.exists():
            errors['data'].append(f'***** Data file not found. Given path: {data_file_path} *****')
        

        # checking script paths/files exist and that scripts are in approved locations
        for elem in config_elements:
            script_element = elem.findall('script')
            if script_element:
                for se in script_element:
                    if se.attrib['src'] == "system":
                        if elem.tag == 'metric':
                            script_path = Path(files.get_global_path() / 'librec_auto' / 'core' / 'cmd' / 'eval')
                        elif elem.tag == 'post':
                            script_path = Path(files.get_global_path() / 'librec_auto' / 'core' / 'cmd' / 'post')
                        else:
                            errors['script'].append(f'***** Scripts not allowed in {elem.tag} section. *****')
                    else:
                        script_path = Path(se.attrib['src'])
                    script_name = se.find('script-name')
                    script_path = Path(script_path / script_name.text)
                    if not script_path.exists():
                        errors['script'].append(f'***** Script {script_name.text} not found in given path. *****')
            # else: if there aren't script elements do nothing, for now

        if 'optimize' in curr_elem:
            alg = single_xpath(config_xml, '/librec-auto/alg')
            if alg is not None:
                for elem in alg:
                    if not elem.getchildren():
                        # for now continue, should add check to make sure value
                        # from reference xml and config xml are same type.
                        continue
                    else:
                        children = [e.tag for e in elem.iterchildren()]
                        if 'value' in children: # impossible case: librec-auto setup catches this first. 
                            errors['optimize'].append(f'***** value tags not allowed in optimize element *****')
                        else:
                            if 'lower' and 'upper' in children:
                                # all good
                                continue
                            else:
                                errors['optimize'].append(f'***** lower and upper elements missing'
                                                          f' from {elem.tag}. Found: {children} *****')

            else:
                errors['elements'].append(f'***** <alg> missing in config file, but optimize is there? *****')
            
        # clear the check elements from before, if present
        check_element = output_tree.find('check')
        if check_element is not None:
            output_tree.remove(check_element)
                
        # If there's anything in the dictionary, there's errors. 
        # Still have checks for if the study was ran for further tests. 
        if list(errors.keys()):
            if not study_ran: # if the output file doesn't exist
                check_tree = etree.SubElement(output_tree, "check")
                for error in errors.keys():
                    for val in errors[error]:
                        message_element = etree.SubElement(check_tree, "message", {'error': error})
                        message_element.text = val
            else: # if it does
                check_tree = etree.Element("check")
                for error in errors.keys():
                    for val in errors[error]:
                        message_element = etree.SubElement(check_tree, "message", {'error': error})
                        message_element.text = val
                # inserting at index 2 because 0 is exp count, and 1 is datetime
                output_tree.insert(2, check_tree) 
        else:
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
            log_object = LogFile(config.get_files().get_exp_paths(i), study_ran)
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
                                message_element = etree.SubElement(check_tree, "message", {'src': error, 
                                                                                           'logline': str(line_number),
                                                                                           'exp_num': str(i)})
                                message_element.text = message.strip('\n')
                    else:
                        message_element = etree.SubElement(check_tree, "message")
                        message_element.text = f"No errors found in experiment {i} logs"
                else:
                    message_element = etree.SubElement(check_tree, "message")
                    message_element.text = f"No errors found in experiment {i} logs"
                

        # open and parse log that was created in main
        librec_auto_log = str(Path(pwd) / "LibRec-Auto_log.log")
        with open(librec_auto_log, 'r') as log_file:
            check_tree = output_tree.find('check')
            if check_tree is not None:
                if not os.stat(librec_auto_log).st_size == 0:
                    for line in log_file:
                        new_line = line.strip('\n')
                        message_element = etree.SubElement(check_tree, "message", {'src': "LibRec-Auto_Log"})
                        message_element.text = new_line
                else:
                    message_element = etree.SubElement(check_tree, "message")
                    message_element.text = "No warnings found in log"
            log_file.close()





        output_tree.getroottree().write(output_xml_path, pretty_print=True)

        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(output_xml_path, parser)
        tree.write(output_xml_path, encoding='utf-8', pretty_print=True)

        self._status = Cmd.STATUS_COMPLETE

    def is_path_legal(self, pathname):
        if os.path.exists(pathname):
            # the file exists and is there
            print("file found")
            return True
        elif os.access(os.path.dirname(pathname), os.W_OK):
            # the file does not exist but there is write access
            print("writable access to dir, file not found")
            return True
        else:
            # the file and/or path do not exist
            print("do not have write permissions to directory")
            return False

    def is_ignorable_error(self, message):
        '''
        This function can be updated with any other errors deemed 'ignorable' by 
        creating a regex string and elif block.
        '''
        property_file_error_pattern = r'.*java\.io\.FileNotFoundException: exp\d*/conf/librec\.properties.*'
        if re.match(property_file_error_pattern, message):
            return True
        return False
    

