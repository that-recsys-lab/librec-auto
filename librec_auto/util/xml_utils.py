from lxml import etree
import copy

def build_parent_path(elem, pathsofar=''):
    nextpath = '/' + elem.tag + pathsofar
    if (elem.getparent() == None):
        return nextpath
    elif (type(elem) is not etree._Element):
        return nextpath
    else:
        return build_parent_path(elem.getparent(), nextpath)

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
        xml_data = etree.fromstring(txt)
    except etree.XMLSyntaxError as e:
        print ("Error parsing XML")
        print ("LXML error in line: {0}".format(e.lineno))
        xml_data = None

    return xml_data

# The idea is that we have a complete element lib_elem and a partial element mod_elem.
# The mod_elem contents override those in lib_elem when they overlap.
def merge_elements(lib_elem, mod_elem):
    print(lib_elem)
    print(mod_elem)
    lib = copy.deepcopy(lib_elem)
    mod = copy.deepcopy(mod_elem)

    for lchild in lib.iterchildren(tag=etree.Element):
        mchild_lst = [child for child in mod.iterchildren(lchild.tag)]
        if len(mchild_lst) > 0:
            lchild.clear()
            lchild.getparent().replace(lchild, mchild_lst[0])
    return lib
