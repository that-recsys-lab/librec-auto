#!/usr/bin/python
import sys
import pandas as pd

target = sys.argv[1]
study_path = sys.argv[2]
filename = sys.argv[3]
perl_script = study_path + "/triple_format_to_libfm.pl"

print("Filename is", filename)

data = pd.read_csv(study_path + "/data/" + filename, sep=",")
data = data.iloc[:, [0, 1, 2]]
columns = [0, 1, 2]
data.columns = columns

user_dict = {}
count = 1
for i in data[0]:
    if i not in user_dict:
        user_dict[i] = count
        count = count + 1

item_dict = {}
count = 1
for i in data[1]:
    if i not in item_dict:
        item_dict[i] = count
        count = count + 1

data.loc[:, 0] = data.apply(lambda x: user_dict[x[0]], axis=1)
data.loc[:, 1] = data.apply(lambda x: item_dict[x[1]], axis=1)

data.to_csv(study_path + "/data/" + filename, header=None, index=False)
print(f"File modified and saved")