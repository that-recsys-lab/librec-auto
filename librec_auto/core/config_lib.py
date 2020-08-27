from collections import OrderedDict
from librec_auto.core.util import Files, utils
import logging
import itertools
from pathlib import Path


class ConfigLib:

    _xml = None
    _element_dict = None
    _source_path = None

    def read_xml(self, path_str):
        path = Path(path_str)
        if (path.exists()):
            xml_input = utils.xml_load_from_path(path)
            return xml_input
        else:
            return None

    def __init__(self, path):
        self._source_path = path
        self._xml = self.read_xml(path)
        self.build_element_dict()

    def build_element_dict(self):
        self._element_dict = {}
        xml_contents = self._xml['librec-auto-library']
        for elem_type in xml_contents.keys():
            elems = utils.force_list(xml_contents[elem_type])
            for elem in elems:
                if '@name' in elem:
                    name = elem['@name']
                    if name not in self._element_dict:
                        self._element_dict[name] = elem
                    else:
                        print(
                            f'librec-auto: WARNING: Name {name} is not unique in {self._source_path}'
                        )
                else:
                    print(
                        f'librec-auto: WARNING: Element {elem} has no name in {self._source_path}'
                    )

    def exists_element(self, ref):
        return ref in self._element_dict

    def get_element(self, ref):
        return self._element_dict[ref]


# Library are searched in inverse order from when they are added. Most recent have priority.
class ConfigLibCollection:

    _libs = []

    def __init__(self):
        pass

    def append(self, lib):
        self._libs = [lib] + self._libs

    def exists_element(self, ref):
        return any([lib.exists_element() for lib in self._libs])

    def get_element(self, ref):
        for lib in self._libs:
            if lib.exists_element(ref):
                return lib.get_element(ref)
        # Should probably throw a key not found error
        return None
