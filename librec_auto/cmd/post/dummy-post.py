# Dummy post
# This script just reqad the input and outputs success

import argparse
import os
import re
import pandas as pd
from librec_auto import read_config_file

def read_args():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(description='Generic post-processing script')
    parser.add_argument('conf', help='Path to configuration file')
    parser.add_argument('target', help='Experiment target')
    parser.add_argument('post', help='Path to post-processing output directory')

    input_args = parser.parse_args()
    return vars(input_args)


if __name__ == '__main__':
    args = read_args()
    config = read_config_file(args['conf'], args['target'])
    result_files = enumerate_results(args['original'])

    file_count = 1
    for file in result_files:
        file_path = pathlib.Path(file)
        if file_path.exists():
            df = pd.read_csv(file)

            outfile = args['result']
            outfilename = f'out-{file_count}.txt'
            df.to_csv(outfilename)
            file_count += 1