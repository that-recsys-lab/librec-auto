import logging
from librec_auto.core.util.xml_utils import xml_load_from_path


class LibraryColl:

    _libraries = []

    # Add to front so the last library listed is consulted first
    def add_lib(self, lib):
        self._libraries.insert(0, lib)

    def get_elem(self, name):
        for lib in self._libraries:
            #            print(f'Checking library {lib.lib_path}')
            elem = lib.get_elem(name)
            if elem is not None:
                return elem
        return None


class Library:

    _xml = None
    _elem_dict = {}

    lib_path = None

    # Read in the library: if src="system", then look in the rules folder
    # Otherwise look in the config folder

    # WK - 2021-7-15: Currently, library files can only be kept in conf 
    # directory due to path being set from files.get_lib_path(), update 
    # to set path based on configuration file's library element.
    def __init__(self, filename, source, files):
        if source and source == 'system':
            path = files.get_lib_path()
        elif source:  # But not 'system'
            # logging.warning(
            #     f'Only system src attribute supported. Got {source}')
            path = files.get_config_dir_path()
        else:
            path = files.get_config_dir_path()

        self.lib_path = path / filename
        if self.lib_path.is_file():
            self._xml = xml_load_from_path(self.lib_path)
            self.build_element_dict()
        else:
            logging.warning(f'The library {self.lib_path} does not exist.')

    def __str__(self):
        return f'Library({self.lib_path.name})'

    def build_element_dict(self):
        for child in self._xml:
            name = child.get('name')
            if name:
                child.attrib.pop('name')
                self._elem_dict[name] = child
            else:
                logging.warning('Library element has no name. Skipping.')

    def get_elem(self, name):
        if name in self._elem_dict:
            return self._elem_dict[name]
        else:
            return None
