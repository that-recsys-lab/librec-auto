import dropbox as db
import argparse
from librec_auto.core.util.encrypt import decrypt_from_file
import getpass
from pathlib import Path


def dropbox_send_file(filepath, destpath, api_key):
    dropbox_api = db.Dropbox(api_key)
    filename = filepath.name
    destname = destpath / filename
    with open(filepath, "rb") as f:
        dropbox_api.files_upload(f.read(),
                                 str(destname),
                                 db.files.WriteMode.overwrite,
                                 mute=False)


def dropbox_send_folder(filepath, destpath, api_key):
    dropbox_api = db.Dropbox(api_key)
    for file in filepath.iterdir():
        destname = destpath / file.name
        with open(file) as f:
            dropbox_api.files_upload(f.read(),
                                     str(destname),
                                     db.files.WriteMode.overwrite,
                                     mute=True)


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
    parser = argparse.ArgumentParser(
        description="Dropbox Post-Processing script")
    parser.add_argument('conf', help='Path to configuration file')
    parser.add_argument("--option",
                        help='Which actions you want to do',
                        choices=["file", "folder", "No"])
    parser.add_argument('--encrypted_key', help="Encrpyted slack api key file")
    parser.add_argument('--path', help="File/folder to post")
    parser.add_argument('--dest', help="Destination file/folder")
    parser.add_argument('--password', help="Password to encrypted API key")

    input_args = parser.parse_args()
    return vars(input_args)


if __name__ == '__main__':
    args = read_args()
    action = args["option"]

    encrypted_file = args['encrypted_key']
    filename = args['path']
    destname = args['dest']

    pw = args['password']
    if pw == None:
        pw = getpass.getpass(f'Password for {encrypted_file}:')

    api_key_bytes = decrypt_from_file(encrypted_file, pw)
    api_key = api_key_bytes.decode('utf-8')

    filepath = Path(filename)
    destpath = Path(destname)

    if action == "file":
        dropbox_send_file(filepath, destpath, api_key)
    elif action == "folder":
        dropbox_send_folder(filepath, destpath, api_key)
    elif action == "No":
        exit()
