from datetime import datetime
from librec_auto.core.util.xml_utils import xml_load_from_path, single_xpath
from collections import defaultdict
from pprint import pprint as pp

from lxml import etree
from .status import move_field_from_element

class ExperimentData:
    '''
    The Python metric data from an experiment.
    '''

    def __init__(self, experiment, exp_name):
        # create name attribute for various post-processing uses
        self._name = exp_name
        # Used for storing parameters changed
        self._param = []
        # Dictionary mapping paramters to their values, for each experiment
        self._param_vals = {}
        # Dicitonary of lists to keep track of metric values
        self._metric_info = defaultdict(list)
        # Dictionary with metric as key and average metric value as value
        self._metric_avg = {}

        # Parameters
        params = experiment.xpath('meta/param')
        for i, param in enumerate(params):
            # getting names of adjusted parameters
            self._param.append(param.find('name').text)
            # print(self._param)
            # getting values each paramter was set to
            self._param_vals[self._param[i]] = float(param.find('value').text)
        

        # Folds
        folds = experiment.xpath('results/folds')

        for fold in folds:
            self._kcv_count = len(fold)
            for cv in fold:
                for met in cv.getchildren():
                    # Add each 
                    self._metric_info[met.attrib['name']].append(float(met.text))
        # pp(self._metric_info)
        
        # Averages
        averages = experiment.xpath('results/averages')
        for ave in averages:
            for met in ave.getchildren():
                self._metric_avg[met.attrib['name']] = float(met.text)

        # pp(self._metric_avg)


class StudyStatus:
    '''
    The output (metrics) from a study.
    '''
    _EXP_DIR_FORMAT = "exp{:05d}"

    def __init__(self, config):
        self._config = config
        self._experiments = {}

        status_path = config.get_files().get_status_path()
        study_xml = None
        if status_path.exists():
            study_xml = xml_load_from_path(status_path)
        
        # First check if the study xml exists.
        if study_xml is None:
            # If it doesn't, create one
            create_study_output(config)
            study_xml = xml_load_from_path(status_path)

        time = single_xpath(study_xml, 'completed_at')
        self._timestamp = time.text
                    
        for exp in study_xml.xpath('//experiment'):
            # keep track of experiment's name
            exp_name = self._EXP_DIR_FORMAT.format(int(exp.attrib['count']))
            self._experiments[exp_name] = ExperimentData(exp, exp_name)
            
        #pp(self._experiments)

    # get metric names: keys from metric_info dict
    # get averages: take metric name as argument
    # get exp_params: return list of (parameter name, value), input experiment number
    # get parameter names

    def get_metric_names(self):
        curr = self._experiments['exp00000']
        return list(curr._metric_info.keys())

    def get_metric_averages(self, metric):
        avgs = []
        for exp in sorted(self._experiments.keys()):
            avgs.append(self._experiments[exp]._metric_avg[metric])
        return avgs

    def get_metric_folds(self, experiment, metric):
        return self._experiments[experiment]._metric_info[metric]

    def get_exp_param_values(self, experiment):
        if not experiment in self._experiments.keys():
            print(f'** Error: ** Invalid experiment name: {experiment}')
            return
        
        param_value_list = []
        exp_params = self._experiments[experiment]._param_vals
        for param in sorted(exp_params.keys()):
            param_value_list.append((param, exp_params[param]))
        return param_value_list

    def get_exp_params(self):
        curr = self._experiments['exp00000']
        return sorted(curr._param)


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
