import argparse
import os
import os.path
from os import path
from pathlib import Path, WindowsPath
import sys
import pandas as pd
from numpy import loadtxt


def run_libFM(target, study_path, split_count):
    curr_path = study_path + "/" + target
    if not path.exists(curr_path + "/libFM.exe"):
        raise Exception("LibFM application does not exist")

    for i in range(1, int(split_count) + 1):
        data = pd.read_csv(curr_path + "/data/split/cv_" + str(i) + "/test.txt", header=None, sep="\t")
        users = data[0].unique()
        items = data[1].unique()
        df = pd.MultiIndex.from_product([users, items], names=[0, 1])
        df = pd.DataFrame(index=df).reset_index()

        print("Cross product created - ", i)
        df = pd.merge(df, data, how='left', on=[0, 1])
        df.fillna(0, inplace=True)
        df.to_csv(curr_path + "/data/split/cv_" + str(i) + "/test.txt", header=None, index=False, sep="\t")
        print("File saved - ", i)

    for i in range(1, int(split_count) + 1):
        data = pd.read_csv(curr_path + "/data/split/cv_" + str(i) + "/test.txt", header=None, sep="\t")
        data[0] = data[0].apply(lambda x: str(0) + ":" + str(int(x)))
        data[1] = data[1].apply(lambda x: str(int(x)) + ":" + str(1))

        df = data[[2, 0, 1]].copy()
        df.to_csv(curr_path + "/data/split/cv_" + str(i) + "/test.txt.libfm", sep=" ", header=None, index=False)
        print("Converting to libfm for test.txt", i)

        data = pd.read_csv(curr_path + "/data/split/cv_" + str(i) + "/train.txt", header=None, sep="\t")
        data[0] = data[0].apply(lambda x: str(0) + ":" + str(int(x)))
        data[1] = data[1].apply(lambda x: str(int(x)) + ":" + str(1))

        df = data[[2, 0, 1]].copy()
        df.to_csv(curr_path + "/data/split/cv_" + str(i) + "/train.txt.libfm", sep=" ", header=None, index=False)
        print("Converting to libfm for train.txt", i)

    for i in range(1, int(split_count) + 1):
        params3 = curr_path + "/libFM -task r -train " + curr_path + "/data/split/cv_" + str(
            i) + "/train.txt.libfm -test " + curr_path + "/data/split/cv_" + str(
            i) + "/test.txt.libfm -dim '1,1,20' -out " + curr_path + "/data/split/cv_" + str(i) + "/output.txt"
        pl_script3 = os.popen(params3)
        for line in pl_script3:
            print(line.rstrip())

    for i in range(1, int(split_count) + 1):
        data = pd.read_csv(curr_path + "/data/split/cv_" + str(i) + "/test.txt", header=None, sep="\t")
        output = loadtxt(curr_path + "/data/split/cv_" + str(i) + "/output.txt", unpack=False)
        print("Merging the output - ", i)
        data[2] = output
        data.to_csv(curr_path + "/exp00000/result/out-" + str(i) + ".txt", sep=",", header=None, index=False)


def read_args():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(
        description="Extract the experimental parameters")
    parser.add_argument('target', help='Target folder')
    parser.add_argument('filename', help='File name')
    parser.add_argument('study_path', help='Path for target study')
    parser.add_argument('split_count', help='Total split counts')
    input_args = parser.parse_args()
    return vars(input_args)


if __name__ == '__main__':
    args = read_args()
    run_libFM(args['target'], args['study_path'], args['split_count'])
