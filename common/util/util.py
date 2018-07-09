import logging
import sys
import json
import requests
import os
import slackweb
from requests_toolbelt import MultipartEncoder

graph_url = 'https://graph.facebook.com/v2.6/me/messages'

access_token = str(os.environ.get("PAGE_ACCESS_TOKEN", None))


def log(message, params=None, location=None):  # simple wrapper for logging to stdout on heroku
    if location is not None:
        print('\n[{0}]'.format(location))

    if type(params) is None:
        print(' ' + str(message))
    else:
        print(' ' + str(message))

        if type(params) == list:
            for i in params:
                print(' ' + str(i))
        else:
            print(params)
    sys.stdout.flush()


def mark_seen(sender_id):
    try:
        params = {
            "access_token": access_token
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": sender_id
            },
            "sender_action": "mark_seen"
        })

        requests.post(graph_url, params=params, headers=headers, data=data)

    except Exception:
        logging.exception('Error at: ' + str(__name__))


def send_message(sender_id, content):
    try:
        params = {
            "access_token": access_token
        }

        if content[-3:] == 'png':
            data = {
                'recipient': json.dumps({
                    'id': sender_id
                }),
                'message': json.dumps({
                    'attachment': {
                        'type': 'image',
                        'payload': {}
                    }
                }),
                'filedata': (os.path.basename(content), open(content, 'rb'), 'image/png')
            }

            # multipart encode the entire payload
            multipart_data = MultipartEncoder(data)

            # multipart header from multipart_data
            multipart_header = {
                'Content-Type': multipart_data.content_type
            }

            requests.post(graph_url, params=params, headers=multipart_header, data=multipart_data)
        else:
            headers = {
                "Content-Type": "application/json"

            }

            data = json.dumps({
                "recipient": {
                    "id": sender_id
                },
                "message": {
                    "text": content
                }
            })
            requests.post(graph_url, params=params, headers=headers, data=data)
    except Exception:
        logging.exception('Error at: ' + str(__name__))


def send_typing_on(sender_id):
    try:
        params = {
            "access_token": access_token
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": sender_id
            },
            "sender_action": "typing_on"
        })

        requests.post(graph_url, params=params, headers=headers, data=data)
    except:
        logging.exception('')


def send_typing_off(sender_id):
    try:
        params = {
            "access_token": access_token
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": sender_id
            },
            "sender_action": "typing_off"
        })
        requests.post(graph_url, params=params, headers=headers, data=data)
    except Exception:
        logging.exception('Error at: ' + str(__name__))


def send_to_slack(message):
    slack_master = slackweb.Slack(url="https://hooks.slack.com/services/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")
    slack_master.notify(text=message)


def send_to_slack_suicide_illness(message):
    try:
        channel = slackweb.Slack(url="https://hooks.slack.com/services/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")
        channel.notify(text=message)
    except Exception:
        logging.exception('Error at: ' + str(__name__))


def send_quick_replies(sender_id, quick_replies_title, quick_replies, payload='DEFAULT'):
    try:
        params = {
            "access_token": os.environ["PAGE_ACCESS_TOKEN"]
        }

        headers = {
            "Content-Type": "application/json"
        }

        q_res_list = []
        for idx, i in enumerate(quick_replies):
            q_res_list.append(
                {
                    "content_type": "text",
                    "title": quick_replies[idx],
                    "payload": payload
                }
            )

        data = json.dumps({
            "recipient": {
                "id": sender_id
            },
            "message": {
                "text": quick_replies_title,
                "quick_replies": q_res_list
            }
        })
        requests.post(graph_url, params=params, headers=headers, data=data)
    except:
        logging.exception('')


def deduplicate_preserving_order(original_list):
    seen = set()
    seen_add = seen.add
    return [x for x in original_list if not (x in seen or seen_add(x))]
