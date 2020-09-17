import argparse
from librec_auto.core.util.encrypt import encrypt
import getpass
from pathlib import Path


def encrypt_file(infile, outfile, password):
    with open(infile, "rb") as api:
        data = api.read()

    encrypted = encrypt(data, password)
    with open(outfile, "wb") as encry:
        encry.write(encrypted)

def read_args():
    parser = argparse.ArgumentParser(description="API key encryption for librec-auto")
    parser.add_argument('--encrypted', help="location to store encrypted file")
    parser.add_argument('--key', help="location of API key file")
    parser.add_argument('--password', help="Password (prompt if omitted)")

    input_args = parser.parse_args()
    return vars(input_args)

if __name__ == '__main__':
    args = read_args()
    keyfile = args["key"]
    encrypted = args['encrypted']

    pw = args['password']
    if pw == None:
        pw = getpass.getpass(f'Password for {encrypted}:')

    inpath = Path(keyfile)
    if inpath.exists():
        encrypt_file(inpath, encrypted, pw)
    else:
        print(f'Key file {keyfile} does not exist. Exiting.')
        exit(-1)

    exit(0)
