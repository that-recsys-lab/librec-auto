# No-op rerank
# This script just copies the input to the output, but it shows how such a script should work

import argparse
import os
import re
import pandas as pd
from librec_auto import ConfigCmd


def read_args():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(description='Generic re-ranking script')
    parser.add_argument('conf', help='Path to configuration file')
    parser.add_argument('target', help='Experiment target')
    parser.add_argument('original', help='Path to original results directory')
    parser.add_argument('result', help='Path to results output directory')

    input_args = parser.parse_args()
    return vars(input_args)


RESULT_FILE_PATTERN = 'out-\d+.txt'


def enumerate_results(result_path):
    files = os.listdir(result_path)
    pat = re.compile(RESULT_FILE_PATTERN)
    return [file for file in files if pat.match(file)]


def read_config_file(args):
    config_file = args['conf']
    target = args['target']

    config = ConfigCmd(config_file, target)
    config.process_config()
    return config


if __name__ == '__main__':
    args = read_args()
    config = read_config_file(args)
    result_files = enumerate_results(args['original'])

    file_count = 1
    for file in result_files:
        df = pd.read_csv(file)

        outfile = args['result']
        outfilename = f'out-{file_count}.txt'
        df.to_csv(outfilename)
        file_count += 1
