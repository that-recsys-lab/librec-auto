# No-op rerank
# This script just copies the input to the output, but it shows how such a script should work

import argparse
import os
import re
import pandas as pd
from librec_auto import read_config_file
import pathlib


def read_args():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(description='Generic re-ranking script')
    parser.add_argument('conf', help='Name of configuration file')
    parser.add_argument('target', help='Experiment target')
    parser.add_argument('original', help='Path to original results directory')
    parser.add_argument('result', help='Path to destination results directory')
    parser.add_argument('--max_len', help='The maximum number of items to return in each list')
    parser.add_argument('--another_param', help='Another parameter passed to the script.')

    input_args = parser.parse_args()
    return vars(input_args)


RESULT_FILE_PATTERN = 'out-\d+.txt'

def enumerate_results(result_path):
    files = os.listdir(result_path)
    pat = re.compile(RESULT_FILE_PATTERN)
    return [file for file in files if pat.match(file)]


if __name__ == '__main__':
    args = read_args()
    config = read_config_file(args['conf'], args['target'])
    result_files = enumerate_results(args['original'])

    print("Sample re-ranking script")
    print(f'\tGot parameter max_len: {args["max_len"]}')
    print(f'\tGot parameter another_parameter: {args["another_param"]}')

    file_count = 1
    for file in result_files:
        file_path = pathlib.Path(file)
        if file_path.exists():
            df = pd.read_csv(file)

            # Do the re-ranking here

            outfile = args['result']
            outfilename = f'out-{file_count}.txt'
            df.to_csv(outfilename)
            file_count += 1
