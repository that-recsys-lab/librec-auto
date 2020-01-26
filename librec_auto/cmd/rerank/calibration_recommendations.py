# No-op rerank
# This script just copies the input to the output, but it shows how such a script should work

import argparse
import os
import re
import pandas as pd
from librec_auto import read_config_file
import pathlib
from librec_auto.cmd.rerank.calibrated_common_funcs import *


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
INPUT_FILE_PATTERN = 'cv_\d+'

def enumerate_results(result_path):
    files = os.listdir(result_path)
    pat = re.compile(RESULT_FILE_PATTERN)
    return [file for file in files if pat.match(file)]


if __name__ == '__main__':
    args = read_args()
    print(args)
    config = read_config_file(args['conf'], args['target'])
    result_files = enumerate_results(args['original'])

    split_path = config.get_files().get_split_path()
    # split_names = os.listdir(split_path)

    # kind of a hack!
    f_path = pathlib.Path(args['target'] + "/data/genres.csv")
    if f_path.exists():
        f_df = pd.read_csv(f_path, names=['movieid', 'genre'], sep='\t')

    print("Sample re-ranking script")
    print(f'\tGot parameter max_len: {args["max_len"]}')
    print(f'\tGot parameter another_parameter: {args["another_param"]}')

    for file_name in result_files:

        # reading the result
        input_file_path = pathlib.Path(args['original'] + '/' + file_name)

        # reading the training set
        cv_path = str(split_path) + '/cv_' + re.findall('\d+', file_name)[0] + '/train.txt'
        tr_file_path = pathlib.Path(cv_path)


        if tr_file_path.exists():
            tr_df = pd.read_csv(tr_file_path, names=['userid', 'itemid', 'score'], sep='\t')

        if input_file_path.exists():
            recoms_df = pd.read_csv(input_file_path, names=['userid', 'itemid', 'score'])

            # Do the re-ranking here
            # df = a_function(df)
            reranked_df = execute(recoms_df, tr_df, f_df)

            output_file_path = pathlib.Path(args['result'] + '/' + file_name)
            print('Reranking for ', output_file_path)
            reranked_df.to_csv(output_file_path, header=None, index=False)
