from librec_auto.core.cmd import Cmd
from librec_auto.core.config_cmd import ConfigCmd
from librec_auto.core.util import Status, Files
from librec_auto.core.util.xml_utils import single_xpath
import os
from pathlib import Path
from lxml import etree


# what to check for
# 1. paths are legal (include paths to scripts). Include both "system" and user-defined
#       Path
# 2. we have write permission to files and directories
# 3. no necessary elements are missing: data, splitter, alg, metric
# 4. if optimize then there must be upper/lower parameters in alg 
#    Must NOT be value elements
# 5. if there's a library reference, the reference must exist. 
# 6. (eventually) XML validation against schema
# 7. (eventually) validate script parameters. 
# 8. (eventually) fix Java side so that sheck command doesn't load all files

# What to check for:
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

        print("Checking for all necessary elements.")
        curr_elem = [e.tag for e in config_xml.getchildren()]
        necc_elem = {'data': 'Data section',
                     'splitter': 'Splitter section', 
                     'alg': 'Algorithm section',
                     'metric': 'Metric section'}
        for elem in necc_elem.keys():
            if elem not in curr_elem:
                print(f'** {necc_elem[elem]} missing in config file. **')

        print("\nChecking path to library.")
        library = single_xpath(config_xml, '/librec-auto/library')
        print(f'Given file: {library.text}\n')
        if library.attrib['src'] == "system":
            lib_path = Path(files.get_lib_path() / library.text)
        else:
            lib_path = Path(library.attrib['src'] / library.text)
        if not lib_path.exists():
            print(f'Library not found. Given path: {lib_path}')
        if not os.access(lib_path, os.W_OK):
            print("Write access not granted in data directory.")
        
        print("Checking path to data.")
        data_dir = single_xpath(config_xml, '/librec-auto/data/data-dir')
        data_dir_path = Path(pwd / data_dir.text)
        print(f'Given directory: {data_dir_path}')
        print(f'Directory exists? {data_dir_path.exists()}')
        data_file = single_xpath(config_xml, '/librec-auto/data/data-file')
        print(f'Given file: {data_file.text}')
        data_file_path = Path(data_dir_path / data_file.text)
        print(f'File exists? {data_file_path.exists()}\n')
        if not data_file_path.exists():
            print(f'Data file not found. Given path: {data_file_path}')
        if not os.access(data_file_path, os.W_OK):
            print("Write access not granted in data directory.")

        print("Checking path(s) to script(s).")
        for elem in config_xml.getchildren():
            script_element = elem.findall('script')
            if script_element is not None:
                # if script_element.attrib['src'] == "system":
                #     script_path = 
                for se in script_element:
                    script_name = se.find('script-name')
                    print(script_name.text)

        # print("Checking for optimizations.")
        # optimization = single_xpath(config_xml, 'librec-auto/optimize')
        # if optimization is not None:
        #     algo = single_xpath(config_xml, 'librec-auto/alg')
        #     found_upper_lower = False
        #     for elem in algo.iterchildren():
        #         if elem.getchildren() is None:
        #             print(elem.text)
        #         else:
        #             for val in elem.iterchildren():
        #                 print(val)


        
        

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



