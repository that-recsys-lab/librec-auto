from lxml import etree
from inspect import getsourcefile
from os.path import abspath
from pathlib import Path
import logging

# TODO: Replace with XPath
def safe_xml_path(config, key_list):
    """
    Checks that the list of keys in key_list can be used to navigate through
    the dictionaries in config.

    :param config: a nested dictionary structure
    :param path_list: a list of dictionary keys
    :return: True if the sequence of keys is valid
    """
    dct = config
    for elem in key_list:
        if elem in dct:
            dct = dct[elem]
        else:
            return False
    return True

# TODO: Replace with XPath
def extract_from_path(config, key_list):
    """
    Retrieves element content by following the path in key_list.

    :param config: a nested dictionary structure
    :param path_list: a list of dictionary keys
    :return: Element at the end of the sequence
    """
    dct = config
    for elem in key_list:
        if elem in dct:
            dct = dct[elem]
        else:
            return None
    return dct


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
            print ('please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False


def get_script_path(script_xml, cmd_type):
    script_path = '.'
    if script_xml['@lang'] != 'python3':
        print(f'librec-auto: Only Python3 scripts currently supported. Got {script_xml["@lang"]}.')
        return None
    if '@src' in script_xml:
        if script_xml['@src'] == 'system':
            script_path = Path(abspath(getsourcefile(lambda:0))).parent.parent / 'cmd' / cmd_type
        else:
            script_path = force_path(script_xml['@src'])
    if 'script-name' in script_xml:
        return script_path / script_xml['script-name']
    else:
        return None

def create_param_spec(param_dict):
    return [f'--{key}={val}' for key, val in param_dict.items()]

