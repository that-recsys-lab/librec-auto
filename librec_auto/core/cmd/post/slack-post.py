import sys
import slack as sl
from slacker import Slacker

import argparse
from pathlib2 import Path

import matplotlib
matplotlib.use('Agg')  # For non-windowed plotting
import matplotlib.pyplot as plt


def slack_send_message(message):
    #slack = Slacker('xoxb-625375728051-787189332448-Ufqx4usZgQUW9c3q3J0JsH7o')
    slack = Slacker(slack_cmd)
    slack.chat.post_message('#la_bot', message)


#Zijun: This is function for auto send file and comments to slack
def slack_send_file(rep, fil1, tit1):
    #client = sl.WebClient(token='xoxb-625375728051-787189332448-Ufqx4usZgQUW9c3q3J0JsH7o')
    client = sl.WebClient(token=slack_cmd)
    with open(rep, 'rb') as att:
        r = client.api_call("files.upload",
                            files={
                                'file': att,
                            },
                            data={
                                'channels': '#la_bot',
                                'filename': fil1,
                                'title': tit1,
                                'initial_comment': 'This is {}'.format(fil1),
                            })
    assert r.status_code == 200


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

if __name__ == '__main__':
    slack_cmd = str(sys.argv[2])

    if len(sys.argv) < 2:
        print("Argument input fail")

    parser = argparse.ArgumentParser()

    parser.add_argument("action", choices=["message", "file"])
    parser.add_argument("API-Token", type=str)
    parser.add_argument("content")

    args = parser.parse_args()
    dictargs = vars(args)

    if dictargs["action"] == "message":
        post_message = sys.argv[3]
        slack_send_message(post_message)
    if dictargs["action"] == "file":
        file_directory = sys.argv[3]
        slack_send_file(file_directory, "The file is here", "Plot")
