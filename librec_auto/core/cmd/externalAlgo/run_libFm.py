import argparse
import os
import os.path
import random
from os import path
from pathlib import Path, WindowsPath
import sys
import pandas as pd
import numpy as np
from numpy import loadtxt
import csv


def run_libFM(target, study_path, split_count, filename):
    curr_path = study_path + "/" + target
    if not path.exists(curr_path + "/libFM.exe"):
        raise Exception("LibFM application does not exist")

    data = pd.read_csv(curr_path + "/data/" + filename, header=None, sep=",")
    data[0] = data[0].apply(lambda x: str(0) + ":" + str(int(x)))
    data[1] = data[1].apply(lambda x: str(int(x)) + ":" + str(1))
    if len(data.columns) == 3:
        df = data[[2, 0, 1]].copy()
    else:
        length = len(data.columns)
        for j in range(3, length):
            data[j] = data[j].apply(lambda x: str(int(x)) + ":" + str(j) if int(x) != 0 else np.nan)
        li = [2, 0, 1] + [*range(3, length)]
        df = data[li].copy()

        cols = [*range(3, length)]
        df["new"] = df[cols].apply(lambda x: ' '.join(x.dropna()), axis=1)
        df = df[[2, 0, 1, 'new']]

    print("Converting to libfm.. ")
    df.to_csv(curr_path + "/data/" + filename + ".libfm", sep=" ", header=None, index=False, quoting=csv.QUOTE_NONE, escapechar=' ')

    for i in range(1, int(split_count) + 1):
        # If features have to be added.
        # Appending the features in the file
        test = pd.read_csv(curr_path + "/data/split/cv_" + str(i) + "/test.txt", header=None, sep="\t")
        test.to_csv(curr_path + "/data/split/cv_" + str(i) + "/test_new.txt", header=None, index=False, sep="\t")
        if filename != "":
            # Cross product creation: Sampling 100 values
            users = test[0].unique()
            items = test[1].unique()

            df_dict = test.to_dict(orient="index")
            user_dict = {}
            for val in users:
                user_dict[val] = []

            {user_dict[v[0]].append(v[1]) for (k, v) in df_dict.items()}
            total_sample = 100
            df = pd.DataFrame([], columns=[0, 1])
            for val in users:
                items_present = user_dict[val]
                items_ex = list(set(items) - set(items_present))
                it = random.sample(list(items_ex), total_sample)
                total_items = items_present + it
                df1 = pd.MultiIndex.from_product([[val], total_items], names=[0, 1])
                df1 = pd.DataFrame(index=df1).reset_index()
                df = df.append(df1, ignore_index=True)

            print("Cross product created")
            df = pd.merge(df.astype(str), test.astype(str), how='left', on=[0, 1])
            df.fillna(0, inplace=True)
            df.to_csv(curr_path + "/data/split/cv_" + str(i) + "/test.txt", header=None, index=False, sep="\t")

            # Appending the features
            data = pd.read_csv(curr_path + "/data/" + filename + ".libfm", header=None, sep=" ")
            data.drop_duplicates(subset=[1, 2], inplace=True)

            test = pd.read_csv(curr_path + "/data/split/cv_" + str(i) + "/test.txt", header=None, sep="\t")
            test[0] = test[0].apply(lambda x: str(0) + ":" + str(int(x)))
            test[1] = test[1].apply(lambda x: str(int(x)) + ":" + str(1))
            li = [2, 0, 1]
            test_new = test[li].copy()
            test_new.columns = [0, 1, 2]
            data_merged = pd.merge(test_new, data, how='left', on=[1, 2])
            data_merged = data_merged.drop(['0_y'], axis=1)
            data_merged.to_csv(curr_path + "/data/split/cv_" + str(i) + "/test.txt.libfm", header=None, index=False, sep=" ")
            print("Converting to test.txt.libfm.. - ", i)

            train = pd.read_csv(curr_path + "/data/split/cv_" + str(i) + "/train.txt", header=None, sep="\t")
            train.to_csv(curr_path + "/data/split/cv_" + str(i) + "/train_new.txt", header=None, index=False, sep="\t")
            train[0] = train[0].apply(lambda x: str(0) + ":" + str(int(x)))
            train[1] = train[1].apply(lambda x: str(int(x)) + ":" + str(1))
            li = [2, 0, 1]
            train_new = train[li].copy()
            train_new.columns = [0, 1, 2]
            data_merged = pd.merge(train_new, data, how='left', on=[1, 2])
            data_merged = data_merged.drop(['0_y'], axis=1)
            data_merged.to_csv(curr_path + "/data/split/cv_" + str(i) + "/train.txt.libfm", header=None, index=False, sep=" ")
            print("Converting to Train.txt.libfm.. - ", i)

        # No feature append. Create cross product for test.txt.
        else:
            users = test[0].unique()
            items = test[1].unique()

            df_dict = test.to_dict(orient="index")
            user_dict = {}
            for val in users:
                user_dict[val] = []

            {user_dict[v[0]].append(v[1]) for (k, v) in df_dict.items()}
            total_sample = 100
            df = pd.DataFrame([], columns=[0, 1])
            for val in users:
                items_present = user_dict[val]
                items_ex = list(set(items) - set(items_present))
                it = random.sample(list(items_ex), total_sample)
                total_items = items_present + it
                df1 = pd.MultiIndex.from_product([[val], total_items], names=[0, 1])
                df1 = pd.DataFrame(index=df1).reset_index()
                df = df.append(df1, ignore_index=True)
            df = pd.merge(df.astype(str), test.astype(str), how='left', on=[0, 1])
            df.fillna(0, inplace=True)

            df.to_csv(curr_path + "/data/split/cv_" + str(i) + "/test.txt", header=None, index=False, sep="\t")

            #Converting to libfm
            test = pd.read_csv(curr_path + "/data/split/cv_" + str(i) + "/test.txt", header=None, sep="\t")
            test.to_csv(curr_path + "/data/split/cv_" + str(i) + "/test_new.txt", header=None, index=False, sep="\t")
            test[0] = test[0].apply(lambda x: str(0) + ":" + str(int(x)))
            test[1] = test[1].apply(lambda x: str(int(x)) + ":" + str(1))
            li = [2, 0, 1]
            test_new = test[li].copy()
            test_new.columns = [0, 1, 2]
            test_new.to_csv(curr_path + "/data/split/cv_" + str(i) + "/test.txt.libfm", header=None, index=False, sep=" ")
            print("Converting to test.txt.libfm.. - ", i)

            train = pd.read_csv(curr_path + "/data/split/cv_" + str(i) + "/train.txt", header=None, sep="\t")
            train.to_csv(curr_path + "/data/split/cv_" + str(i) + "/train_new.txt", header=None, index=False, sep="\t")
            train[0] = train[0].apply(lambda x: str(0) + ":" + str(int(x)))
            train[1] = train[1].apply(lambda x: str(int(x)) + ":" + str(1))
            li = [2, 0, 1]
            train_new = train[li].copy()
            train_new.columns = [0, 1, 2]
            train_new.to_csv(curr_path + "/data/split/cv_" + str(i) + "/train.txt.libfm", header=None, index=False, sep=" ")
            print("Converting to Train.txt.libfm.. - ", i)

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
    parser.add_argument('libfm_filename', help='LibFM File name')
    parser.add_argument('study_path', help='Path for target study')
    parser.add_argument('split_count', help='Total split counts')
    input_args = parser.parse_args()
    return vars(input_args)


if __name__ == '__main__':
    args = read_args()
    run_libFM(args['target'], args['study_path'], args['split_count'], args['libfm_filename'])
