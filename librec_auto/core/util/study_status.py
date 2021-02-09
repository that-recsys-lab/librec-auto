from datetime import datetime

from lxml import etree
from .status import move_field_from_element


def create_study_output(config) -> None:
    """Creates a study-wide output.xml file

    Args:
        config (ConfigCmd): The config file for this study
    """
    study_path = config.get_files().get_study_path()
    output_file_path = str(study_path / "output.xml")

    # Create the root level tree.
    output_tree = etree.Element("study")

    # Add an experiment count element at the root level.
    experiment_count_element = etree.SubElement(output_tree,
                                                "experiment_count")
    experiment_count_element.text = str(config.get_sub_exp_count())

    # Add a completion timestamp.
    completion_timestamp_element = etree.SubElement(output_tree,
                                                    "completed_at")
    completion_timestamp_element.text = str(datetime.now())

    # Add an element to contain the experiments results.
    experiments_element = etree.SubElement(output_tree, "experiments")

    # Adds the config.xml content to the output.xml file.
    study_config_path = config.get_files().get_config_file_path()

    study_config_element = etree.parse(str(study_config_path)).getroot()
    study_config_element.tag = 'config'  # Rename the tag to 'config'

    # Add a comment to the config element.
    comment = etree.Comment(
        ' This is the configuration used to run the study. ')
    study_config_element.insert(1, comment)

    # Add config to output_tree
    move_field_from_element(study_config_element, None, output_tree)

    # For each experiment number...
    for i in range(0, config.get_sub_exp_count()):

        # Get the experiment's output path.
        output_path = str(
            config.get_files().get_exp_paths(i).get_path('output'))

        experiment_xml_root = etree.parse(output_path).getroot()

        # Remove statuses from the experiment tree.
        move_field_from_element(experiment_xml_root, "statuses")

        move_field_from_element(experiment_xml_root, None, experiments_element)

    # Save/write the output tree.
    output_tree.getroottree().write(output_file_path, pretty_print=True)

    # These three lines reload the XML file to properly format it.
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(output_file_path, parser)
    tree.write(output_file_path, encoding='utf-8', pretty_print=True)
