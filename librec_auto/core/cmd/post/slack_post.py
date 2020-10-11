from slack import WebClient
import argparse
from librec_auto.core.util.encrypt import decrypt_from_file
import getpass


def slack_send_message(message, channel, slack_api):
    client = WebClient(token=slack_api)
    client.chat_postMessage(channel=channel, text=message)


def slack_send_file(filename, message, channel, slack_api):
    client = WebClient(token=slack_api)
    with open(filename, 'rb') as att:
        r = client.api_call("files.upload",
                            files={
                                'file': att,
                            },
                            data={
                                'channels': channel,
                                'filename': filename,
                                'title': f'File: {filename}',
                                'initial_comment': message
                            })
    assert r.status_code == 200


'''
Zijun:
    About how to run this file. 
    There are two action for the slack to recognize. The first one is the message. The second one is the file

    message:
        Description: If you want to direct post a sentence in to the slack channel. 
        The command should like this:
        python slack_post.py [action] [API-Token] ["Expression"]
        eg: python slack_post.py message xoxb-625375728051-787189332448-Ufqx4usZgQUW9c3q3J0JsH7o "Hello World"

    file: 
        Description: If you want to post file into slack.
        The command should like this:
        python slack_post.py [action] [API-Token] /directory
        eg: python slack_post.py file xoxb-625375728051-787189332448-Ufqx4usZgQUW9c3q3J0JsH7o /directory/---.py

'''


def read_args():
    parser = argparse.ArgumentParser(
        description="Slack Post-Processing script")
    parser.add_argument('conf', help='Path to configuration file')
    parser.add_argument("--option",
                        help='Which actions you want to do',
                        choices=["message", "file", "No"])
    parser.add_argument('--channel', help='Which channel you want to post')
    parser.add_argument('--encrypted_key', help="Encrpyted slack api key file")
    parser.add_argument('--file', help="File to post")
    parser.add_argument('--password', help="Password to encrypted API key")
    parser.add_argument('--message', help="Message to post")

    input_args = parser.parse_args()
    return vars(input_args)


if __name__ == '__main__':
    args = read_args()
    action = args["option"]

    channel = args['channel']
    encrypted_file = args['encrypted_key']
    filename = args['file']
    message = args['message']

    pw = args['password']
    if pw == None:
        pw = getpass.getpass(f'Password for {encrypted_file}:')

    api_key_bytes = decrypt_from_file(encrypted_file, pw)
    api_key = api_key_bytes.decode('utf-8')

    if action == "message":
        slack_send_message(message, channel, api_key)
    elif action == "file":
        slack_send_file(filename, message, channel, api_key)
    elif action == "No":
        exit()
