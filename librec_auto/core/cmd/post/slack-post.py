import sys
import slack as sl
from slacker import Slacker

import argparse
from pathlib2 import Path

import matplotlib

matplotlib.use('Agg')  # For non-windowed plotting
import matplotlib.pyplot as plt

# This is decrypted function
from cryptography.fernet import Fernet


def slack_send_message(message, channel, slack_api):
    # slack = Slacker('xoxb-625375728051-787189332448-Ufqx4usZgQUW9c3q3J0JsH7o')
    slack = Slacker(slack_api)
    slack.chat.post_message(channel, message)


# Zijun: This is function for auto send file and comments to slack
def slack_send_file(rep, fil1, tit1, channel, slack_api):
    # client = sl.WebClient(token='xoxb-625375728051-787189332448-Ufqx4usZgQUW9c3q3J0JsH7o')
    client = sl.WebClient(token=slack_api)
    with open(rep, 'rb') as att:
        r = client.api_call("files.upload", files={'file': att, },
                            data={'channels': channel, 'filename': fil1, 'title': tit1,
                                  'initial_comment': 'This is {}'.format(fil1), }
                            )
    assert r.status_code == 200


def decrypted_function(key1, encrypted_file, decrypted_file):
    file = open(key1, "rb")
    key = file.read()
    file.close()

    with open(encrypted_file, "rb") as api:
        data = api.read()
    fernet = Fernet(key)
    encrypted = fernet.decrypt(data)
    with open(decrypted_file, "wb") as decry:
        decry.write(encrypted)


'''
Zijun:
    About how to run this file. 
    There are two action for the slack to recognize. The first one is the message. The second one is the file

    message:
        Description: If you want to direct post a sentence in to the slack channel. 
        The command should like this:
        python slack-post.py [action] [API-Token] ["Expression"]
        eg: python slack-post.py message xoxb-625375728051-787189332448-Ufqx4usZgQUW9c3q3J0JsH7o "Hello World"

    file: 
        Description: If you want to post file into slack.
        The command should like this:
        python slack-post.py [action] [API-Token] /directory
        eg: python slack-post.py file xoxb-625375728051-787189332448-Ufqx4usZgQUW9c3q3J0JsH7o /directory/---.py

'''


def read_args():
    parser = argparse.ArgumentParser(description="Slack Post-Processing script")
    parser.add_argument('conf', help='Path to configuration file')
    parser.add_argument('target', help='Experiment target')
    parser.add_argument("--option", help='Which actions you want to do', choices=["message", "file", "No"])
    parser.add_argument('--channel', help='Which channel you want to post')
    parser.add_argument('--decrypted_file', help="repository of decrypted slack api key file")
    parser.add_argument('--encrypted_file', help="repository of encrpyted slack api key file")
    parser.add_argument('--key', help="repository of key file")
    parser.add_argument('--information', help="What information you want to post to slack")

    input_args = parser.parse_args()
    return vars(input_args)


if __name__ == '__main__':
    args = read_args()
    action = args["option"]

    channel = args['channel']
    decrypted_file = args['decrypted_file']
    encrypted_file = args['encrypted_file']
    key_file = args['key']

    information = args['information']

    if action == "message":
        decrypted_function(key_file, encrypted_file, decrypted_file)
        with open(decrypted_file, "r") as file:
            slack_api = file.read()
        slack_send_message(information, channel, slack_api)
    elif action == "file":
        decrypted_function(key_file, encrypted_file, decrypted_file)
        with open(decrypted_file, "r") as file:
            slack_api = file.read()
        slack_send_file(information, "The file is here", "Plot", channel, slack_api)
    elif action == "No":
        exit()


