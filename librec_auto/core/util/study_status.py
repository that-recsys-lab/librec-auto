from datetime import datetime
# from librec_auto.core.util.files import ExpPaths, Files
from librec_auto.core.util.xml_utils import xml_load_from_path, single_xpath
from collections import defaultdict
from pprint import pprint as pp

from lxml import etree
from .status import move_field_from_element

class ExperimentData:
    '''
    The Python metric data from an experiment.
    '''

    def __init__(self, experiment):
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
        print("vals:")
        for fold in folds:
            for cv in fold:
                for met in cv.getchildren():
                    # Add each 
                    self._metric_info[met.attrib['name']].append(float(met.text))
        pp(self._metric_info)
        
        # Averages
        averages = experiment.xpath('results/averages')
        print("averages:")
        for ave in averages:
            for met in ave.getchildren():
                self._metric_avg[met.attrib['name']] = float(met.text)

        pp(self._metric_avg)


class StudyStatus:
    '''
    The output (status) from a study.
    '''

    def __init__(self, config):
        self._config = config
        self._experiments = {}
        study_xml = xml_load_from_path(config.get_files().get_status_path())
        
        # First check if the study xml exists.
        if study_xml is None:
            # If it doesn't, create one
            create_study_output(config)
            study_xml = xml_load_from_path(config.get_files().get_status_path())
                    
        for exp in study_xml.xpath('//experiment'):
            # keep track of experiment's name
            exp_name = "exp" + exp.attrib['count']
            
            self._experiments[exp_name] = ExperimentData(exp)
            
        pp(self._experiments)
            
            






def create_study_output(config) -> None:
    """Creates a study-wide output.xml file

    Args:
        config (ConfigCmd): The config file for this study
    """
    study_path = config.get_files().get_study_path()
    output_file_path = str(study_path / "output.xml")


    # Create the root level tree.
    output_tree = etree.Element("study")

    # Add an experiment count element at the root level.
    experiment_count_element = etree.SubElement(output_tree,
                                                "experiment_count")
    experiment_count_element.text = str(config.get_sub_exp_count())

    # Add a completion timestamp.
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

        experiment_xml_root = etree.parse(output_path).getroot()

        # Remove statuses from the experiment tree.
        move_field_from_element(experiment_xml_root, "statuses")

        move_field_from_element(experiment_xml_root, None, experiments_element)

    # Save/write the output tree.
    output_tree.getroottree().write(output_file_path, pretty_print=True)

    # These three lines reload the XML file to properly format it.
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(output_file_path, parser)
    tree.write(output_file_path, encoding='utf-8', pretty_print=True)
