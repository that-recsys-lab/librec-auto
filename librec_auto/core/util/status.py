import datetime
import os.path
from pathlib import Path
from librec_auto.core.util import xml_load_from_path, force_list, ExpPaths, LogFile
from librec_auto.core.util.xml_utils import single_xpath
from lxml import etree

# A .status file looks like this
# <librec-auto-status>
#    <message>Completed</message>
#    <exp-no>1</exp-no>\
#    <param><name>rec.neighbors.knn.number</name><value>30</value></param>
#    <date>June 28, 11:00 PM</date>
# </librec-auto-status>
# TODO: Rewrite with lxml. This is kind of embarrassing.


class Status():
    def __init__(self, sub_paths):
        self._subpaths = sub_paths
        status_path = self._subpaths.get_path('status')

        if status_path.exists():
            self._name = sub_paths.exp_name
            self._status_xml = xml_load_from_path(status_path)
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
    def save_status(msg, exp_count, config, paths):
        status_xml = etree.Element("librec-auto-status")
        msg_elem = etree.SubElement(status_xml, "message")
        msg_elem.text = msg
        expno_elem = etree.SubElement(status_xml, "exp_no")
        expno_elem.text = str(exp_count)
        date_elem = etree.SubElement(status_xml, "date")
        date_elem.text = str(datetime.datetime.now())

        conf_xml = config.get_files().get_exp_paths(exp_count).get_study_conf()
        var_elems = conf_xml.xpath("//*[@var='true']")
        for var_elem in var_elems:
            if var_elem.tag == 'param':
                var_name = var_elem.get('name')
            else:
                var_name = var_elem.tag
            var_value = var_elem.text

            param_elem = etree.SubElement(status_xml, "param")

            name_elem = etree.SubElement(param_elem, "name")
            name_elem.text = var_name
            value_elem = etree.SubElement(param_elem, "value")
            value_elem.text = var_value

        status_file = paths.get_path('status')

        # write to status file
        status_xml.getroottree().write(status_file.absolute().as_posix(),
                                       pretty_print=True)

        # get the output file
        output_file = paths.get_path('output')

        output_file_path_string = paths.get_path(
            'output').absolute().as_posix()

        _update_output(output_file_path_string, status_xml)


def _update_output(output_file_path: str, status_xml: etree._Element) -> None:
    """
    Saves or updates the output file with this Status object's new status. 
    """
    status_xml.tag = "status"
    if _output_file_exists(output_file_path):
        # append this status to an existing file
        parser = etree.XMLParser(
            remove_blank_text=True
        )  # using a custom parser lets us pretty print later
        tree = etree.parse(output_file_path, parser)  # open existing file
        root = tree.getroot()
        statuses_element = root.find('statuses')  # get the statuses element
        statuses_element.append(
            status_xml)  # append this new status to the end
        tree.write(output_file_path,
                   pretty_print=True)  # re-write the original tree
    else:
        # create a new output tree
        output_xml = etree.Element("librec-auto-output")
        output_xml.append(
            etree.Comment(
                'DO NOT EDIT. File automatically generated by librec-auto'))
        statuses_element = etree.SubElement(
            output_xml, "statuses")  # add a statuses object
        statuses_element.append(
            status_xml
        )  # add this status as a subelement to the statuses object

        # write to output XML
        output_xml.getroottree().write(output_file_path, pretty_print=True)


def _output_file_exists(path: str) -> bool:
    """
    Checks if the output file already exists
    """
    if not os.path.isfile(path):
        return False
    return True


# # Accept list of vars and tuples
# @staticmethod
# def save_status(msg, exp_count, config, paths):
#     status_file = paths.get_path('status')
#     status_front = Status._TEMPLATE_FRONT.format(msg, exp_count, datetime.datetime.now())
#
#     status_params = ''
#     conf_xml = config.get_files().get_sub_paths(exp_count).get_exp_conf()
#     var_elems = conf_xml.xpath("//*[@var='true']")
#     for var_elem in var_elems:
#         if var_elem.tag == 'param':
#             var_name = var_elem.get('name')
#         else:
#             var_name = var_elem.tag
#         var_value = var_elem.text
#
#         status_params = status_params + Status._TEMPLATE_LINE.format(var_name, var_value)
#
#     status_info = Status._HEADER + status_front + status_params + Status._TEMPLATE_END
#
#     with status_file.open(mode='w') as fh:
#         fh.write(str(status_info))
