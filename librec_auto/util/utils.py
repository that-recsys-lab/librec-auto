from pathlib2 import Path
from librec_auto.util import xmltodict


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


def read_xml_from_path_string(path_str):
    path = Path(path_str)
    return xml_load_from_path(path)


def xml_load_from_path(path):
    """
    Loads the XML file in a dictionary

    Prints a warning and returns an empty dictionary if the file can't be read.
    :param path: The file name
    :return: A dictionary with the XML rules
     """
    try:
        with path.open() as fd:
            txt = fd.read()
    except IOError as e:
        print ("Error reading ", path)
        print ("IO error({0}): {1}".format(e.errno, e.strerror))
        # logging.error("Error reading %s. IO error: (%d) %s", path, e.errno, e.strerror)
        return {}

    return xml_load_from_text(txt)


def xml_load_from_text(txt):
    try:
        xml_data = xmltodict.parse(txt)
    except xmltodict.expat.ExpatError as e:
        print ("Error parsing XML")
        print ("Expat error in line: {0}".format(e.lineno))
        # logging.error("Error parsing XML. Expat error in line %d", e.lineno)
        xml_data = {}

    return xml_data