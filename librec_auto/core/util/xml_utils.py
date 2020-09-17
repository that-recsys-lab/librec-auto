from lxml import etree
from pathlib import Path
import copy
import logging


def build_parent_path(elem, pathsofar=''):
    if elem.tag == 'param':  # params are distinguished by name attributes
        pathsofar = f"[@name='{elem.get('name')}']"
    nextpath = '/' + elem.tag + pathsofar
    if (elem.getparent() == None):
        return nextpath
    elif (type(elem) is not etree._Element):
        return nextpath
    else:
        return build_parent_path(elem.getparent(), nextpath)


def read_xml_from_path_string(path_str):
    path = Path(path_str)
    if path.exists():
        return xml_load_from_path(path)
    else:
        logging.error(f'XML file {path_str} does not exist. Load failed.')
        return None


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
        print("Error reading ", path)
        print("IO error({0}): {1}".format(e.errno, e.strerror))
        # logging.error("Error reading %s. IO error: (%d) %s", path, e.errno, e.strerror)
        return None

    return xml_load_from_text(txt)


def xml_load_from_text(txt):
    try:
        parser = etree.XMLParser(remove_comments=True)
        xml_data = etree.fromstring(txt, parser=parser)
    except etree.XMLSyntaxError as e:
        print("Error parsing XML")
        print("LXML error in line: {0}".format(e.lineno))
        xml_data = None

    return xml_data


# The idea is that we have a complete element lib_elem and a partial element mod_elem.
# The mod_elem contents override those in lib_elem when they overlap.
# Only works at the top-level of children in the element.
def merge_elements(lib_elem, mod_elem):
    lib = copy.deepcopy(lib_elem)
    mod = copy.deepcopy(mod_elem)

    lib_tags = [child.tag for child in lib.iterchildren(tag=etree.Element)]
    mod_tags = [child.tag for child in mod.iterchildren(tag=etree.Element)]

    mod_extra = list(set(mod_tags).difference(set(lib_tags)))

    for lchild in lib.iterchildren(tag=etree.Element):
        mchild_lst = [child for child in mod.iterchildren(lchild.tag)]
        if len(mchild_lst) > 0:
            lchild.clear()
            lchild.getparent().replace(lchild, mchild_lst[0])

    for extra_tag in mod_extra:
        matching = [child for child in mod.iterchildren(tag=extra_tag)]
        lib.append(matching[0])

    return lib


def single_xpath(elem, path):
    ans = elem.xpath(path)
    if len(ans) > 0:
        return ans[0]
    else:
        return None
