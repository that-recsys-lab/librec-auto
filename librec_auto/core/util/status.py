import datetime
import os.path
from librec_auto.core.util import xml_load_from_path, ExpPaths, LogFile
from librec_auto.core.util.xml_utils import single_xpath
from lxml import etree


class Status():
    """
    The output (status) from an experiment.
    """
    def __init__(self, sub_paths: ExpPaths):
        self._subpaths = sub_paths
        output_path = self._subpaths.get_path('output')

        if output_path.exists():
            self._name = sub_paths.exp_name
            self._status_xml = xml_load_from_path(output_path)
            self._message = single_xpath(self._status_xml,
                                         '/librec-auto-status/message').text

        if self._subpaths.get_path('log').exists():
            self._log = LogFile(self._subpaths)
        else:
            self._log = None

            params = self._status_xml.xpath('//param')
            if params != None:
                self.process_params(params)
            else:
                self._params = []
                self.m_vals = []

    def __str__(self):
        params_string = self.get_params_string()
        if self._log:
            results_string = self.get_log_info()
        else:
            results_string = "No LibRec results"
        return f'Status({self._name}:{self._message}{params_string} Overall{results_string})'

    def is_completed(self):
        return self._message == 'Completed'

    def process_params(self, param_elements):
        param_list = []
        val_list = []

        # Maybe could be done with an ugly list comprehension
        for param_xml in param_elements:
            name_elem = single_xpath(param_xml, 'name')
            param_list.append(name_elem.text)
            val_elem = single_xpath(param_xml, 'value')
            val_list.append(val_elem.text)

        self._params = param_list
        self._vals = val_list

    def get_params_string(self):
        params_string = ''
        if self._params == []:
            return " No parameters"
        for param, val in zip(self._params, self._vals):
            params_string += f' {param}: {val}'
        return params_string

    def get_log_info(self):
        kcv_count = self._log.get_kcv_count()
        if kcv_count is None:
            return self.get_metric_info(self._log, 0)
        else:
            return self.get_metric_info(self._log, -1)

    def get_metric_info(self, log, idx):
        metric_info = ''
        for metric_name in log.get_metrics():
            metric_value = log.get_metric_values(metric_name)[idx]
            metric_info = metric_info + f' {metric_name}: {float(metric_value):.3f}'
        return metric_info

    @staticmethod
    def save_status(msg: str, exp_count: int, config, paths: ExpPaths) -> None:
        """Generate and save the experiment status

        Args:
            msg (str): The message for this status. i.e. "Executing"
            exp_count (int): The experiment count within the study, zero indexed.
            config (ConfigCmd): The configuration for this experiment.
            paths (ExpPaths): The paths object for this experiment.
        """
        status_xml = etree.Element("librec-auto-status")

        message_element = etree.SubElement(status_xml, "message")
        message_element.text = msg

        experiment_number_element = etree.SubElement(status_xml, "exp_no")
        experiment_number_element.text = str(exp_count)

        date_element = etree.SubElement(status_xml, "date")
        date_element.text = str(datetime.datetime.now())

        conf_xml = config.get_files().get_exp_paths(exp_count).get_study_conf()

        variable_elements = conf_xml.xpath("//*[@var='true']")

        for variable_element in variable_elements:
            if variable_element.tag == 'param':
                variable_name = variable_element.get('name')
            else:
                variable_name = variable_element.tag
            variable_value = variable_element.text

            parameter_element = etree.SubElement(status_xml, "param")

            name_element = etree.SubElement(parameter_element, "name")
            name_element.text = variable_name
            value_element = etree.SubElement(parameter_element, "value")
            value_element.text = variable_value

        # get the output file
        output_file = paths.get_path('output')

        output_file_path_string = output_file.absolute().as_posix()

        _update_output(output_file_path_string, status_xml, paths)


def _generate_folds_results_output(paths: ExpPaths) -> etree._Element:
    """Generates XML data for CV fold results

    Args:
        paths (ExpPaths): The paths object for this experiment

    Returns:
        etree._Element: An XML tree containing cv fold results
    """
    # check if the log directory exists and has contents
    if not paths.get_path('log').exists() or not os.listdir(
            paths.get_path('log')):
        return
    log = LogFile(paths)
    root_xml = etree.Element("root")
    results_element = etree.SubElement(root_xml, "folds")
    for _, index in enumerate(range(log.get_kcv_count())):
        # using index + 1 to one-index the folds
        cv_element = etree.SubElement(results_element, "cv", id=str(index + 1))
        all_values = log.get_all_values()
        for metric in all_values:
            metric_element = etree.SubElement(cv_element,
                                              "metric",
                                              name=metric)
            metric_element.text = all_values[metric]['cv_results'][
                index]  # add cv value
    return root_xml


def _generate_average_results_output(paths: ExpPaths) -> etree._Element:
    # check if the log directory exists and has contents
    if not paths.get_path('log').exists() or not os.listdir(
            paths.get_path('log')):
        return
    log = LogFile(paths)
    root_xml = etree.Element("root")
    averages_element = etree.SubElement(root_xml, "averages")
    all_values = log.get_all_values()
    for metric in all_values:
        metric_element = etree.SubElement(averages_element,
                                          "metric",
                                          name=metric)
        # add average value
        metric_element.text = all_values[metric]['average_result']
    return root_xml


def _update_output(output_file_path: str, status_xml: etree._Element,
                   paths: ExpPaths) -> None:
    """Saves or updates the output file with this Status object's new status.


    Args:
        output_file_path (str): The path of the output file
        status_xml (etree._Element): The XML for this status update
        paths (ExpPaths): The paths object for this experiment
    """
    status_xml.tag = "status"

    # update the results objects
    results_folds_xml = _generate_folds_results_output(paths)
    results_average_xml = _generate_average_results_output(paths)

    if _output_file_exists(output_file_path):
        # append this status to an existing file
        parser = etree.XMLParser(
            remove_blank_text=True
        )  # using a custom parser lets us pretty print later
        tree = etree.parse(output_file_path, parser)  # open existing file
        root = tree.getroot()
        statuses_element = root.find('statuses')  # get the statuses element
        results_element = root.find('results')  # get the results element

        move_field_from_element(status_xml,
                                'exp_no')  # remove exp_no from status
        move_field_from_element(status_xml,
                                'param')  # remove param from status

        statuses_element.append(
            status_xml)  # append this new status to the end

        if results_folds_xml is not None:
            # remove folds to replace it
            results_fold_element = results_element.find('folds')
            results_element.remove(results_fold_element)

            # put results xml into the tree
            move_field_from_element(results_folds_xml, "folds",
                                    results_element)

        if results_average_xml is not None:
            # remove averages to replace it
            results_fold_element = results_element.find('averages')
            results_element.remove(results_fold_element)

            # put results xml into the tree
            move_field_from_element(results_average_xml, "averages",
                                    results_element)

        tree.write(output_file_path,
                   pretty_print=True)  # re-write the original tree
    else:
        # create a new output tree
        output_xml = etree.Element("experiment")
        output_xml.append(
            etree.Comment(
                'DO NOT EDIT. File automatically generated by librec-auto'))
        meta_element = etree.SubElement(output_xml,
                                        "meta")  # add a meta object
        statuses_element = etree.SubElement(
            output_xml, "statuses")  # add a statuses object

        # set the experiment count attribute
        experiment_number = status_xml.find('exp_no').text
        output_xml.attrib['count'] = experiment_number

        # move param to meta
        move_field_from_element(status_xml, 'param', meta_element)

        statuses_element.append(
            status_xml
        )  # add this status as a subelement to the statuses object

        # add a results object
        results_element = etree.SubElement(output_xml, "results")

        if results_folds_xml is not None:
            move_field_from_element(results_folds_xml,
                                    "folds",
                                    parent=results_element)
        else:
            etree.SubElement(results_element, "folds")

        if results_average_xml is not None:
            move_field_from_element(results_average_xml,
                                    "averages",
                                    parent=results_element)
        else:
            etree.SubElement(results_element, "averages")

        # write to output XML
        output_xml.getroottree().write(output_file_path, pretty_print=True)


def move_field_from_element(
    original_parent: etree._Element,
    to_remove: str,
    replacement_parent: etree._Element = None,
) -> None:
    """ An XML utility function to move or remove a field from an element.
    If replacement_parent is None, this performs a removal.
    Otherwise, it performs a replacement.

    Args:
        original_parent (etree._Element): The initial parent of the field to be moved/removed.
        to_remove (str): The name of the field to be moved/removed. None means to move the root. None can only be used to move and not remove.
        replacement_parent (etree._Element, optional): The new parent for the field to be moved. Defaults to None.
    """
    element_to_move = None
    if to_remove is not None:
        element_to_move = original_parent.find(to_remove)
        element_to_move.getparent().remove(element_to_move)
    else:
        # We want to move the original parent here.
        element_to_move = original_parent

    if replacement_parent is not None or to_remove is None:
        # Replace the element
        replacement_parent.append(element_to_move)


def _output_file_exists(path: str) -> bool:
    """Checks if the output file already exists


    Args:
        path (str): The path to the output file.

    Returns:
        bool: True means that the file exists.
    """
    if not os.path.isfile(path):
        return False
    return True
