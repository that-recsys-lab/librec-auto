import sys
import slack as sl
from slacker import Slacker

import argparse
from pathlib2 import Path

import matplotlib

import dropbox
import sys, os

matplotlib.use('Agg')  # For non-windowed plotting
import matplotlib.pyplot as plt

# This is decrypted function
from cryptography.fernet import Fernet

def dropbox_send_file(rep, file_name, dropbox_api_2):
    dropbox_api = dropbox.Dropbox(dropbox_api_2)
    with open(rep, "rb") as f:
        dropbox_api.files_upload(f.read(), file_name, mute=True)
    print ("Done uploading plot")

def decrypted_file_Dropbox(repo_key, repo_encrypted_Dropbox_file, repo_decrypted_Dropbox_file):
    file = open(repo_key, "rb")
    key = file.read()
    file.close()

    with open(repo_encrypted_Dropbox_file, "rb") as api:
        data = api.read()
    fernet = Fernet(key)
    encrypted = fernet.decrypt(data)
    with open(repo_decrypted_Dropbox_file,"wb") as decry:
        decry.write(encrypted)


'''
Zijun:
    About how to run this file. 
    There are Three options for the Dropbox to recognize. 
    file:
        Description: Post single file to dropbox
        give repo to single file
    folder:
        Description: Post entire folder to dropbox
        give repo to folder to Dropbox
'''


def read_args():
    parser = argparse.ArgumentParser(description="Dropbox Post-Processing script")
    parser.add_argument('conf', help='Path to configuration file')
    parser.add_argument('target', help='Experiment target')
    parser.add_argument("--option", help='Which actions you want to do', choices=["file", "folder", "No"])
    parser.add_argument('--decrypted_Dropbox_file', help="repository of decrypted Dropbox api key file")
    parser.add_argument('--encrypted_Dropbox_file', help="repository of encrpyted Dropbox api key file")
    parser.add_argument('--key', help="repository of key file")
    parser.add_argument('--repository', help="What file you want to post to Dropbox")

    input_args = parser.parse_args()
    return vars(input_args)


if __name__ == '__main__':
    args = read_args()
    action = args["option"]

    decrypted_Dropbox_file = args['decrypted_Dropbox_file']
    encrypted_Dropbox_file = args['encrypted_Dropbox_file']
    key_file = args['key']

    repository = args['repository']

    if action == "file":
        try:
            decrypted_file_Dropbox(key_file, encrypted_Dropbox_file, decrypted_Dropbox_file)
            with open(decrypted_Dropbox_file, "r") as file:
                dropbox_api = file.read()
            dropbox_send_file(repository, "/Recall.png", dropbox_api)
        except Exception as err:
            print("Failed to upload %s\n%s" % (file, err))
    elif action == "folder":
        decrypted_file_Dropbox(key_file, encrypted_Dropbox_file, decrypted_Dropbox_file)
        with open(decrypted_Dropbox_file, "r") as fold:
            dropbox_api = fold.read()
        for dir, dirs, files in os.walk(repository):
            for file in files:
                file_path = os.path.join(dir, file)
                dest_path = os.path.join('/Librec-auto-folder-test', file)
                print ('Uploading %s to %s' % (file_path, dest_path))
                with open(file_path) as f:
                    dropbox_send_file(file_path, dest_path, dropbox_api)
    elif action == "No":
        exit()