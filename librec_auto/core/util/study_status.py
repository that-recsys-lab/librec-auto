import os
from datetime import datetime
from subprocess import check_output
from librec_auto.core.util.xml_utils import xml_load_from_path, single_xpath
from librec_auto.core.util import Files
from pathlib import Path
from collections import defaultdict
from lxml import etree
from .status import move_field_from_element

class ExperimentData:
    '''
    The Python metric data from an experiment.
    '''

    def __init__(self, experiment):
        self.exp_no = int(experiment.attrib['count'])

        # Used for storing parameters changed
        self._param = []
        # Dictionary mapping paramters to their values
        self._param_vals = {}
        # Dicitonary of lists to keep track of metric values
        self._metric_info = defaultdict(list)
        # Dictionary of average metric values
        self._metric_avg = {}

        # Parameters
        params = experiment.xpath('meta/param')
        for i, param in enumerate(params):
            # getting names of adjusted parameters
            self._param.append(param.find('name').text)

            # getting values each paramter was set to
            self._param_vals[self._param[i]] = float(param.find('value').text)

        # Folds
        folds = experiment.xpath('results/folds')
        for fold in folds:
            for cv in fold:
                for met in cv.getchildren():
                    # Add each 
                    self._metric_info[met.attrib['name']].append(float(met.text))
        
        # Averages
        averages = experiment.xpath('results/averages')
        for ave in averages:
            for met in ave.getchildren():
                self._metric_avg[met.attrib['name']] = float(met.text)



class StudyStatus:
    '''
    The output (metrics) from a study.
    '''

    def __init__(self, config):
        self._config = config
        self._experiments = {}

        status_path = config.get_files().get_status_path()
        study_xml = None
        if status_path.exists():
            study_xml = xml_load_from_path(status_path)
        
        # if the output xml has one element it's check, 0 nothing has ran
        # if there's more than that then the experiment ran and user is evaluating
        if len(study_xml.getchildren()) <= 1: 
            create_study_output(config)
            study_xml = xml_load_from_path(status_path)
            
        for exp in study_xml.xpath('//experiment'):
            # keep track of experiment's name
            exp_name = Files.get_exp_name(exp.attrib['count'])
            
            self._experiments[exp_name] = ExperimentData(exp)

        model = single_xpath(study_xml, '/study/config/splitter/model')
        if model.text == 'kcv':
            self._kcv_count = int(model.attrib['count'])
        else:
            self._kcv_count = 0
        time = single_xpath(study_xml, 'completed_at').text
        time_obj = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
        self._timestamp = time_obj.strftime("%Y%m%d_%H%M%S")

    def get_metric_names(self):
        curr = self._experiments[Files.get_exp_name(0)]
        return list(curr._metric_info.keys())

    def get_exp_params(self):
        curr = self._experiments[Files.get_exp_name(0)]
        return curr._param

    def get_metric_averages(self, metric):
        avgs = []
        for exp in self._experiments.values():
            avgs.append(exp._metric_avg[metric])
        return avgs

    def get_exp_param_values(self, experiment):
        if not experiment in self._experiments.keys():
            print(f'** Error: ** Invalid experiment name: {experiment}')
            return []

        param_value_list = []
        exp_params = self._experiments[experiment]._param_vals
        for param in exp_params:
            param_value_list.append((param, exp_params[param]))
        return param_value_list

    def get_metric_folds(self, experiment, metric):
        return self._experiments[experiment]._metric_info[metric]


def check_output_xml(filepath):
    if os.path.exists(filepath):
        doc = xml_load_from_path(Path(filepath))
        num_elements = len(doc.getchildren())
        return num_elements
    return 0
    

def create_study_output(config) -> None:
    """Creates a study-wide output.xml file

    Args:
        config (ConfigCmd): The config file for this study
    """
    
    # 2021-7-19 - WK: rewriting so that if an output xml already exists
    # (which it should if check was ran) these get added to file rather
    # than overwriting
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
