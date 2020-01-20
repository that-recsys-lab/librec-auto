# Dummy post
# This script just reqad the input and outputs success

import argparse
import os
import re
import pandas as pd
from librec_auto import read_config_file
import pathlib
from librec_auto.util import Status


def read_args():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(description='Generic post-processing script')
    parser.add_argument('conf', help='Path to configuration file')
    parser.add_argument('target', help='Experiment target')
    parser.add_argument('--param0', help='Value passed to script')
    parser.add_argument('--param1', help='Value passed to script', default='lorem ipsum')

    input_args = parser.parse_args()
    return vars(input_args)


if __name__ == '__main__':
    args = read_args()
    config = read_config_file(args['conf'], args['target'])

    print("Dummy post script")
    print(f'\tGot parameter param0: {args["param0"]}')
    print(f'\tGot parameter param1: {args["param1"]}')

    for sub_path in config.get_files().get_sub_paths_iterator():
        status = Status(sub_path)
        print(status)

