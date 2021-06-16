import argparse
from pathlib import Path
import shutil
from librec_auto.core.util import confirm


def read_args():
    '''
    Parse command line arguments.
    :return:
    '''
    parser = argparse.ArgumentParser(
        description=
        'The configuration wizard for setting up studies to run under librec-auto.',
        epilog=
        'Refer to documentation at: https://librec-auto.readthedocs.io/en/latest/'
    )

    # Optional with arguments
    parser.add_argument("-s",
                        "--study",
                        help="Use the specified study directory name. Will be created.")

    parser.add_argument("-d",
                        "--data",
                        help="Use the specified data file. Will be copied to the study directory.")

    # read and validate all 3
    # see if  datafile exists
    # see if study exists

    input_args = parser.parse_args()
    return vars(input_args)

# Replaces the data file element in the config file to point to the data file
def copyconfig(config, newfile, datafile):
    # open config file for reading and newfile for writing
    f = open(config, 'r')
    content = f.readlines()

    for i in range(len(content)):
        if content[i].find('data-file') != -1:
            content[i] = '\t\t<data-file format="text">' + datafile + '</data-file>\n'

    f.close()

    w = open(newfile, 'w')
    w.writelines(content)
    w.close()


if __name__ == '__main__':

    args = read_args()

    study_path = None
    data_path = None

    # check data file is valid
    if args["data"]:
        data_file = args["data"]
        data_path = Path(data_file)
        if not data_path.is_file():
            print(f"Error: Cannot find data file: {data_path.absolute()}")  # add name here!!!
            exit(-1)

    # check study directory does not already exist
    if args["study"]:
        study_directory = args["study"]
        study_path = Path(study_directory)
        if study_path.exists():
            del_confirm = \
                confirm(prompt=f"Study directory {study_path.absolute()} already exists. Confirm deletion",
                        resp=False)
            if del_confirm:
                shutil.rmtree(study_directory)
            else:
                print("Study directory not deleted. Exiting.")
                exit(0)

    # check for configuration file
    module_path = Path(__file__).parent.parent
    sample_conf_path = module_path / 'librec_auto' / 'library' / 'sample-config.xml'
    if not sample_conf_path.is_file():
        print(f"Error: Sample Config file is missing at {sample_conf_path}.")
        exit(-1)

    # create new directories
    config_dir = study_path / 'conf'
    config_dir.mkdir(parents=True)
    data_dir = study_path / 'data'
    data_dir.mkdir(parents=True)
    post_dir = study_path / 'post'
    post_dir.mkdir(parents=True)

    # add configuration file
    data_name = str(data_path.name)
    study_config = config_dir / 'config.xml'
    copyconfig(sample_conf_path, study_config, data_name)

    # make copy of data file for data folder
    shutil.copy2(data_path, data_dir)

    print(f'Your study located at {study_path} is ready to run.')
    print('Run the following commands (assumes librec-auto package is installed):')
    print(f'cd {study_path}')
    print('python -m librec_auto run')
    print('When the study completes, the evaluation results can be found in the')
    print(f'directory {post_dir} as CSV files.')
    print('To make changes to your study configuration, edit the configuration file')
    print(f'located at {study_config}. Choose a different algorithm or alternative evaluation metric')
    print('Refer to the documentation at: https://librec-auto.readthedocs.io/en/latest/ for all librec-auto options.')
    print('Enjoy!')

    exit(0)
