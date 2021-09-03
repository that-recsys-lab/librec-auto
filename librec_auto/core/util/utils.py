from lxml import etree
from inspect import getsourcefile
from os.path import abspath
from pathlib import Path
import re
from datetime import datetime
from . import xml_utils
import subprocess
from subprocess import CalledProcessError, DEVNULL
import glob
import os


def force_list(item):
    """
    Ensures that an item is of list type.

    :param item:
    :return: item or [item]
    """
    if (type(item) is list):
        return item
    else:
        return [item]


def force_path(item):
    """
    Ensures that an item is of Path type.

    :param item:
    :return: item or [item]
    """
    if (type(item) is Path):
        return item
    else:
        return Path(item)


def frange(start, stop, step):
    x = start
    while x < stop:
        yield x
        x += step


def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n:
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y:
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True

    """

    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')

    while True:
        # ans = raw_input(prompt)
        ans = input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print('please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False


def get_script_path(script_xml, cmd_type):
    script_path = '.'
    if script_xml.get('lang') != 'python3':
        print(
            f'librec-auto: Only Python3 scripts currently supported. Got {script_xml.get("lang")}.'
        )
        return None
    if script_xml.get('src'):
        if script_xml.get('src') == 'system':
            script_path = Path(abspath(
                getsourcefile(lambda: 0))).parent.parent / 'cmd' / cmd_type
        else:
            script_path = force_path(script_xml.get('src'))
    name_elem = xml_utils.single_xpath(script_xml, 'script-name')
    if name_elem is not None:
        return script_path / name_elem.text
    else:
        return None

def create_param_spec(script_xml):
    params = script_xml.xpath('param')
    param_list = []
    for param in params:
        key = param.get('name')
        if param.text:
            val = param.text
            param_list.append(f'--{key}={val}')
    return param_list

def safe_run_subprocess(process_specs: list, current_working_directory: str):
    """ Safely run a subprocess and check its output for errors
    returns:
        errors: str - if there are errors from running the script, the string
            is returned to be added to output.xml
        0: int - the cript ran and executed normally
        e.returncode: int - if the script has error code exits built in and the
            script returns one, this will catch and return it

    """
    try:
        script_output = subprocess.Popen(process_specs, 
                                         cwd=current_working_directory,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        # check Popen constructor for encoding
        # try with Popen as proc:
        # 
        output, errors = script_output.communicate()
        if errors:
            str_err = str(errors, encoding='utf-8')
            str_err = str_err.strip('<')
            str_err = str_err.strip('>')
            ret_lst = re.split(r'Process Process-\d*:', str_err)
            ret_lst = [x for x in ret_lst if x != '']
            if len(ret_lst) > 1:
                return ret_lst
            return str_err
        else:
            return 0
    except CalledProcessError as e:
        return e.returncode

def create_log_name(filename: str):
    _time = str(datetime.now())
    _time_obj = datetime.strptime(_time, '%Y-%m-%d %H:%M:%S.%f')
    _timestamp = _time_obj.strftime("%Y%m%d_%H%M%S")
    return filename.format(_timestamp)

def purge_old_logs(path: str):
    for file in glob.glob(path):
        if re.match(r'.*/LibRec-Auto_log.*', file):
            os.remove(file)