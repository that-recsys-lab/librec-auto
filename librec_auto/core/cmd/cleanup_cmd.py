import os
from datetime import datetime
from lxml import etree
from pathlib import Path
from librec_auto.core.cmd import Cmd
from librec_auto.core.config_cmd import ConfigCmd
from librec_auto.core.util.status import move_field_from_element
from librec_auto.core.util.xml_utils import xml_load_from_path


def check_output_xml(filepath):
    if os.path.exists(filepath):
        doc = xml_load_from_path(Path(filepath))
        return len(doc.getchildren())
    return 0

class CleanupCmd(Cmd):
    """
    Command used to create study output
    """

    def __str__(self):
        return f"CleanupCmd()"

    def setup(self, args):
        pass

    def dry_run(self, config):
        print(f'librec-auto (DR): Running status command {self}')
    
    def execute(self, config: ConfigCmd):
        study_path = config.get_files().get_study_path()
        output_file_path = str(study_path / "output.xml")
        file_found = False

        output_xml_curr_elems = check_output_xml(output_file_path)

        # Create the root level tree. 
        # if check is there (the only way for one element to be in output.xml)
        # preserve it so it's not overwritten. 
        if output_xml_curr_elems == 1:
            # only check is present in the output file
            output_tree = etree.parse(output_file_path).getroot()
            check_tree = output_tree.find('check')
            file_found = True
        else:
            output_tree = etree.Element("study")
            check_tree = None
        
        # Add an experiment count element at the root level.
        if file_found:
            experiment_count_element = etree.Element("experiment_count")
            experiment_count_element.text = str(config.get_sub_exp_count())
            output_tree.insert(0, experiment_count_element)
        else:
            experiment_count_element = etree.SubElement(output_tree,
                                                        "experiment_count")
            experiment_count_element.text = str(config.get_sub_exp_count())

        # Add a completion timestamp.
        if file_found:
            completion_timestamp_element = etree.Element("completed_at")
            completion_timestamp_element.text = str(datetime.now())
            output_tree.insert(0, completion_timestamp_element)
        else:
            completion_timestamp_element = etree.SubElement(output_tree,
                                                        "completed_at")
            completion_timestamp_element.text = str(datetime.now())
        

        # Add an element to contain the experiments results.
        experiments_element = etree.SubElement(output_tree, "experiments")

        # Adds the config.xml content to the output.xml file.
        study_config_path = config.get_files().get_config_file_path()

        study_config_element = etree.parse(str(study_config_path)).getroot()
        study_config_element.tag = 'config'  # Rename the tag to 'config'

        # Add a comment to the config element.
        comment = etree.Comment(
            ' This is the configuration used to run the study. ')
        study_config_element.insert(1, comment)

        # Add config to output_tree
        move_field_from_element(study_config_element, None, output_tree)

        # For each experiment number...
        for i in range(0, config.get_sub_exp_count()):

            # Get the experiment's output path.
            output_path = str(
                config.get_files().get_exp_paths(i).get_path('output'))
            
            # created if statement to prevent OSError: File Not Found when making
            # output.xml from a thrown error. (output won't exist yet)
            if config.get_files().get_exp_paths(i).get_path('output').exists():
                experiment_xml_root = etree.parse(output_path).getroot()

                # Remove statuses from the experiment tree.
                move_field_from_element(experiment_xml_root, "statuses")

                move_field_from_element(experiment_xml_root, None, experiments_element)

        librec_auto_log = str(study_path / config.get_librec_auto_log_name())
        with open(librec_auto_log, 'r') as log_file:
            if check_tree is not None:
                if not os.stat(librec_auto_log).st_size == 0:
                    for line in log_file:
                        new_line = line.strip('\n')
                        message_element = etree.Element("message", 
                                                {'src': librec_auto_log})
                        message_element.text = new_line
                        check_tree.append(message_element)
                else:
                    message_element = etree.Element("message")
                    message_element.text = "No warnings found in log"
                    check_tree.append(message_element)
            else: 
                check_element = etree.Element("check")
                if not os.stat(librec_auto_log).st_size == 0:
                    for line in log_file:
                        new_line = line.strip('\n')
                        message_element = etree.SubElement(check_element, 
                                                "message", 
                                                {'src': librec_auto_log})
                        message_element.text = new_line
                else:
                    message_element = etree.SubElement(check_element, "message")
                    message_element.text = "No warnings found in log"
                output_tree.insert(2, check_element)
            log_file.close()

        # Save/write the output tree.
        output_tree.getroottree().write(output_file_path, pretty_print=True)

        # These three lines reload the XML file to properly format it.
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(output_file_path, parser)
        tree.write(output_file_path, encoding='utf-8', pretty_print=True)