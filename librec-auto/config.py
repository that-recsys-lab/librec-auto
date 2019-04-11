import xmltodict
import itertools
import logging
import string
from datetime import datetime
from utils import force_list, safe_xml_path, frange


class Config:
    """
    Class for the configuration of librec-auto experiments

    Contains methods for reading a configuration file and processing it to produce an
    experiment specification. Has methods for writing a librec-compatible .properties
    file for the experiment.
    """
    # Class members
    _XML_HEAD = 'librec-auto'
    _ELEMENTS = ['data', 'xform', 'splitter', 'alg', 'metric', 'post-process', 'exp']
    _ANON_ELEMENT_PATTERN = "_UNNAMED{}"
    _PROPERTIES_COMMENT_PATTERN = "Created by librec-auto.\nExperiment: Date: {}\nPath: {}"
    _ANON_ELEMENT_COUNT = 0

    # Instance members
    _exp_dict = {}
    _raw_configuration = {}
    _config_dict = {}

    def __init__(self, exp_path):
        self._exp_path = exp_path

    def from_text(self, txt):
        """
        Populates a config object from a text string
        :param txt:
        :return:
        """
        conf_data = Config._load_from_text(txt)
        logging.info("XML configuration text loaded.")
        self._from_raw_config(conf_data)
        logging.info("Configuration converted")

    def from_file(self, path):
        """
        Populates a config object from a file path
        :param path:
        :return:
        """
        conf_data = Config._load_from_file(path)
        logging.info("XML configuration file loaded.")
        self._from_raw_config(conf_data)
        logging.info("Configuration converted")

    def _from_raw_config(self, conf_data):
        self.set_raw_configuration(conf_data)
        parsed = self.parse_config(conf_data)
        self._config_dict = parsed

    def get_raw_configuration(self):
        return self._raw_configuration

    def set_raw_configuration(self, xml):
        self._raw_configuration = xml

    def to_dict(self):
        return self._config_dict

    def get_data(self, eid):
        if safe_xml_path(self._config_dict, ['data', eid]):
            return self._config_dict['data'][eid]
        else:
            logging.error("Reference to unknown data element %s", eid)
            return {}

    def get_xform(self, eid):
        if safe_xml_path(self._config_dict, ['xform', eid]):
            return self._config_dict['xform'][eid]
        else:
            logging.error("Reference to unknown xform element %s", eid)
            return {}

    def get_splitter(self, eid):
        if safe_xml_path(self._config_dict, ['splitter', eid]):
            return self._config_dict['splitter'][eid]
        else:
            logging.error("Reference to unknown splitter element %s", eid)
            return {}

    def get_algorithm(self, eid):
        if safe_xml_path(self._config_dict, ['alg', eid]):
            return self._config_dict['alg'][eid]
        else:
            logging.error("Reference to unknown algorithm element %s", eid)
            return {}

    def get_metric(self, eid):
        if safe_xml_path(self._config_dict, ['metric', eid]):
            return self._config_dict['metric'][eid]
        else:
            logging.error("Reference to unknown metric element %s", eid)
            return {}

    def get_post_process(self, eid):
        if safe_xml_path(self._config_dict, ['post-process', eid]):
            return self._config_dict['post-process'][eid]
        else:
            logging.error("Reference to unknown post-process element %s", eid)
            return {}

    def get_experiment(self, eid):
        if eid in self._exp_dict:
            return self._exp_dict[eid]
        else:
            logging.error("Reference to unknown experiment element %s", eid)
            return {}

    @staticmethod
    def _load_from_file(path):
        """
        Loads the configuration file in a dictionary

        This is the raw configuration. Prints a warning and returns an empty dictionary
        if the file can't be read.
        :param path: The file name
        :return: A dictionary with the XML data
        """
        try:
            with open(path) as fd:
                txt = fd.read()
        except IOError as e:
            print "Error reading ", path
            print "IO error({0}): {1}".format(e.errno, e.strerror)
            logging.error("Error reading %s. IO error: (%d) %s", path, e.errno, e.strerror)
            return {}

        return Config._load_from_text(txt)

    @staticmethod
    def _load_from_text(txt):
        try:
            conf_data = xmltodict.parse(txt)
        except xmltodict.expat.ExpatError as e:
            print "Error parsing XML"
            print "Expat error in line: {0}".format(e.lineno)
            logging.error("Error parsing XML. Expat error in line %d", e.lineno)
            conf_data = {}

        return conf_data

    # Parses the raw configuration to find the specifications in it
    def parse_config(self, config_data):
        """
        Parses the raw configuration dictionary and returns the system-specific data structure.

        The configuration specification fills out the six entries in the config dictionary:
        _data_dict
        _xform_dict
        _splitter_dict
        _alg_dict
        _post_dict
        _metric_dict
        _exp_dict
        If <include> elements are encountered, these are recursively loaded and parsed. Multiple
        levels of include are not supported.
        """
        raw_configs = [config_data]
        config_dict = {}

        if self._XML_HEAD not in config_data:                    # Incorrect XML
            logging.warning("XML input is not a librec-auto configuration file.")
            return config_dict

        if 'include' in config_data[self._XML_HEAD]:             # Get include references
            for incl in force_list(config_data[self._XML_HEAD]['include']):
                raw_configs.append(Config._load_from_file(incl))
                logging.info("Include file %s loaded.", incl)

        for element in self._ELEMENTS:
            logging.debug("Creating entries for element: %s", element)
            named_elements = Config.create_named(element, raw_configs)
            resolved_elements = Config.resolve_refs(named_elements)
            config_dict[element] = resolved_elements

        self.build_exps(config_dict)

        return config_dict

    @staticmethod
    def create_named(element, configs):
        """
        Takes an element and a list of configuration dictionaries and extracts the named
        entities of the given type.

        :param element: An element name. Expected to be from the _ELEMENTS list
        :param configs: A list of configuration dictionaries
        :return: the dictionary mapping ids to element chunks from the configuration dictionary.

        Elements with id attributes are given generated tokens as ids.
        """
        element_dict = {}

        for config in configs:
            if safe_xml_path(config, [Config._XML_HEAD, element]):
                for chunk in force_list(config[Config._XML_HEAD][element]):
                    if '@id' in chunk:
                        eid = chunk['@id']
                    else:
                        eid = Config.get_new_id()

                    element_dict[eid] = chunk

        return element_dict

    @staticmethod
    def resolve_refs(element_dict):
        """
        Take an element, a dictionary of named elements, and a list of configuration
        dictionaries, and instantiates the entities that refer to named elements.

        :param element_dict: A dictionary with named elements
        :return: element dictionary with references resolved

        Reference resolution in this case means copying the attributes from the referenced element to the
        referring element, but only if there is no value for that attribute already. (Treat as a default that
        can be overridden.
        """

        for eid, data in element_dict.items():
                element_dict[eid] = Config.resolve_ref(data, element_dict)

        return element_dict

    @staticmethod
    def resolve_ref(element, element_dict):
        if element is None:
            return None
        if '@ref' in element:
            ref = element['@ref']
            logging.debug("Resolving reference: %s %s", ref, element)
            if ref in element_dict:
                for parent_key, parent_value in element_dict[ref].items():
                    if parent_key not in element:  # Supply default if not present
                        element[parent_key] = parent_value
                    else:  # if key is present, check that all the entries match in name
                        parent_names = set((subelem['@name'] for subelem in force_list(parent_value)
                                            if '@name' in subelem))
                        child_names = set((subelem['@name'] for subelem in force_list(element[parent_key])
                                           if '@name' in subelem))
                        parent_diff = parent_names.difference(child_names)

                        # if there are named sub-elements in the parent that aren't in the child,
                        # copy them.
                        if len(parent_diff) > 0:
                            subelem_to_copy = [subelem for subelem in force_list(parent_value)
                                               if subelem['@name'] in parent_diff]
                            element[parent_key] = force_list(element[parent_key]) + subelem_to_copy
            else:
                logging.warn("Unresolved reference %s not found in configuration input", ref)
                element['error'] = "unresolved reference"

        return element

    def build_exps(self, config_dict):
        """
        Builds the experiment elements. The steps of each experiment will not have been completely resolved in
        resolve_refs because they are one level deeper in the dictionary.

        The complexity here comes from handling the possibility of iteration and the ability to run several algorithms
        at once, which requires that an experiment be split into several sub-experiments. Canonical naming of these
        sub-experiments is non-trivial, so I am just numbering them, but in the end, this will mean that some experiment
        changes, like changing the iteration range of a parameter are probably best handled through creating new
        experiments. Hmm.
        :param config_dict:
        :return:
        """
        exps = config_dict['exp']
        for eid, exp in exps.items():
            data_elem = exp['data']
            split_elem = exp['splitter']
            alg_elems = force_list(exp['alg'])
            # Optional elements
            if safe_xml_path(exp, ["xform"]):
                xform_elem = exp['xform']
            else:
                xform_elem = None
            if safe_xml_path(exp, ["metric"]):
                metric_elems = force_list(exp['metric'])
            else:
                metric_elems = []
            if safe_xml_path(exp, ["post"]):
                post_elems = force_list(exp['post'])
            else:
                post_elems = []

            data_elem = self.resolve_ref(data_elem, config_dict['data'])
            xform_elem = self.resolve_ref(xform_elem, config_dict['xform'])
            split_elem = self.resolve_ref(split_elem, config_dict['splitter'])
            alg_elems = [self.resolve_ref(alg_elem, config_dict['alg']) for alg_elem in alg_elems]
            metric_elems = [self.resolve_ref(metric_elem, config_dict['metric']) for metric_elem in metric_elems]
            post_elems = [self.resolve_ref(post_elem, config_dict['post-process']) for post_elem in post_elems]

            alg_elems = self.expand_iterations(alg_elems)

            # Create create new experiment ids if there are multiple algorithms.
            if len(alg_elems) == 1:
                self.set_experiment_entry(eid, data_elem, xform_elem, split_elem, alg_elems[0],
                                          metric_elems, post_elems)
            else:
                exp_subids = ["{}-{}".format(eid, i) for i in range(0, len(alg_elems))]

                # Create sub-experiments for multiple algorithms
                # The sub-experiments each have their own dictionary entries. The original experiment is replaced
                # by a list of references. The idea is that if you run that, you are effectively running the collection
                # of the others.
                for i in range(0, len(alg_elems)):
                    self.set_experiment_entry(exp_subids[i], data_elem, xform_elem, split_elem, alg_elems[i],
                                              metric_elems, post_elems)
                sub_exp_refs = [{'@ref': subid} for subid in exp_subids]
                self._exp_dict[eid] = sub_exp_refs

    def set_experiment_entry(self, eid, data_elem, xform_elem, split_elem, alg_elem, metric_elems, post_elems):
        exp_entry = {'@id': eid, 'data': data_elem, 'xform': xform_elem, 'splitter': split_elem, 'alg': alg_elem,
                     'metrics': metric_elems, 'post-process': post_elems}
        self._exp_dict[eid] = exp_entry

    def expand_iterations(self, alg_list):
        """
        If there are any algorithms with iteration parameters, create copies of the algorithm,
        one per iteration.

        Iterations have the form <param name= from= to= by=/>. Only numeric from, to, and by attributes are
        accepted. From and to of the range are inclusing. Alg elements only for the moment, although one could
        make the case for metrics, too. The requirements for the iteration parameter is that from < to, by > 0, and
        (to - from) / by <= 10. No error is signaled if this is violated, but it fails silently and uses just the
        start point of the range. May need to do something more drastic. Another complication will arise if the
        algorithm copies
        :return: updated dictionary
        """
        alg_expansions = []
        for alg in alg_list:
            if safe_xml_path(alg, ["param"]):
                algs = self.process_alg_parameters(alg)
                alg_expansions.append(algs)
            else:
                alg_expansions.append([alg])

        return list(itertools.chain(*alg_expansions))

    def process_alg_parameters(self, alg):
        """
        Processes an algorithm element checking for iteration parameters. Expands at most one, creating multiple
        subexperiments in the process

        :param alg:
        :return: list of algorithms, possibly expanded
        """

        iteration_params = list(itertools.ifilter(lambda (par): safe_xml_path(par, ['@from']),
                                                  force_list(alg['param'])))
        other_params = list(itertools.ifilter(lambda (par): not safe_xml_path(par, ['@from']),
                                              force_list(alg['param'])))

        if len(iteration_params) > 1:
            logging.error("Multiple iteration parameters: %s. Ignoring all but first.", alg['@name'])
            bad_params = [self.create_iter_elems(param, True) for param in iteration_params[1:]]
            iteration_params = iteration_params[0:1]
            other_params = other_params + list(itertools.chain(*bad_params))

        # At this point there should only be a maximum of a single iteration parameter. It could be ill-formed.
        if len(iteration_params) != 0:
            iter_elems = Config.create_iter_elems(iteration_params[0], False)
            alg_expand = []
            for iter_elem in iter_elems:
                params = list(other_params).append(iter_elem)   # Need to make a copy
                new_alg = {'@name': alg['@name'], 'param': params}
                alg_expand.append(new_alg)
        else:
            alg_expand = [alg]

        return alg_expand

    @staticmethod
    def create_iter_elems(param, start_only):
        """
        Creates the elements corresponding to an iteration element.

        :param param:
        :param start_only:
        :return:
        """
        name_attr = param['@name']
        from_attr = float(param['@from'])
        to_attr = float(param['@to'])
        by_attr = float(param['@by'])

        # Sanity check (positive steps only), no more than 10 steps
        # If this test fails, the parameter is replaced by its starting point
        if not start_only:
            if from_attr < to_attr and by_attr > 0 and (to_attr - from_attr) / 10 <= 10:
                logging.info("Parameter iteration found. Adding metrics for range: ")
                param_range = frange(from_attr, to_attr+by_attr, by_attr)
            else:
                logging.warn("Illegal parameter iteration specified: from %f, to %f, by %f",
                             from_attr, to_attr, by_attr)
                param_range = [from_attr]
        else:
            logging.warn("Extra iteration parameters replaced with start point %s")
            param_range = [from_attr]

        iter_elems = [{'@name': name_attr, '#text': param_value} for param_value in param_range]

        return iter_elems

    def to_properties(self, exp_id):
        """
        Creates properties text corresponding to the given experiment
        :param exp_id:
        :return:
        """
        exp_data = self.get_experiment(exp_id)
        txt = self.exp_to_properties(exp_data)
        return txt

    def to_xml(self, exp_id):
        exp_data = self.get_experiment(exp_id)
        txt = xmltodict.unparse(exp_data, pretty=True)
        return txt

    def exp_to_properties(self, exp_data):
        date = datetime.now().isoformat()
        comment_txt = self._PROPERTIES_COMMENT_PATTERN.format(exp_data['id'], date, self._exp_path)
        data_txt = self.data_to_properties(exp_data['data'])
        xform_txt = self.xform_to_properties(exp_data['xform'])
        split_txt = self.split_to_properties(exp_data['split'])
        alg_txt = self.alg_to_properties(exp_data['alg'])
        metric_txt = self.metric_to_properties(exp_data['metric'])

        txt = '\n'.join(comment_txt, data_txt, split_txt, alg_txt, metric_txt)
        return txt
        txt = string.join([comment_txt, data_txt, xform_txt, split_txt, alg_txt, metric_txt], '\n')

    def data_to_properties(self, data_elem):
        return "# Data section"

    def xform_to_properties(self, xform_elem):
        return "# Transform section"

    def split_to_properties(self, data_elem):
        return "# Splitter section"

    def alg_to_properties(self, alg_elem):
        return "# Algorithm section"

    def metric_to_properties(self, metric_elem):
        return "# Metric section"

    @staticmethod
    def get_new_id():
        """
        Produces a new id for configuration elements
        
        :return:
        """
        eid = Config._ANON_ELEMENT_PATTERN.format(Config._ANON_ELEMENT_COUNT)
        Config._ANON_ELEMENT_COUNT = Config._ANON_ELEMENT_COUNT + 1
        return eid
