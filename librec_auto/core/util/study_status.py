from lxml import etree
from .status import move_field_from_element


class StudyStatus():
    """
    Handles study-level status updates
    """
    @staticmethod
    def create_study_output(config) -> None:
        """Creates a study-wide output.xml file

        Args:
            config (ConfigCmd): The config file for this study
        """
        study_path = config.get_files().get_study_path()
        output_file_path = str(study_path / "output.xml")

        output_tree = etree.Element("study")

        # Add an experiment count element at the root level
        experiment_count_element = etree.SubElement(output_tree,
                                                    "experiment_count")
        experiment_count_element.text = str(config.get_sub_exp_count())

        experiments_element = etree.SubElement(output_tree, "experiments")

        for i in range(0, config.get_sub_exp_count()):
            # For each experiment number...

            # Get the experiment's output path
            output_path = str(
                config.get_files().get_exp_paths(i).get_path('output'))

            experiment_xml_root = etree.parse(output_path).getroot()

            move_field_from_element(experiment_xml_root, None,
                                    experiments_element)

        # todo also include content from the config.xml file

        # Save/write the output tree
        output_tree.getroottree().write(output_file_path, pretty_print=True)

        # These three lines reload the XML file to properly format it.
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(output_file_path, parser)
        tree.write(output_file_path, encoding='utf-8', pretty_print=True)
