import logging
import os
from flask import Flask, request, redirect
from core.webhook.message_saver import MessageSaver
from common.util.util import log, mark_seen
from save_access_data import add_access_data
from pprint import pprint

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Verified", 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()

    print("\n[JSON from webhook]")
    pprint(data)

    # check if the message is document, sticker, audio or image. if document, then just mark it as seen and anymore response.
    try:
        if 'attachments' in data['entry'][0]['messaging'][0]['message']:
            sender_id = data['entry'][0]['messaging'][0]['sender']['id']

            MessageSaver.store_message(sender_id, 'ATTACHMENT')

            mark_seen(sender_id)
            return "ok", 200
    except:
        logging.exception('')

    try:
        if data["object"] == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:

                    sender_id = messaging_event["sender"]["id"]

                    mark_seen(sender_id)

                    if messaging_event.get("message"):

                        message_text = str(messaging_event["message"]["text"])

                        if messaging_event['message'].get("quick_reply"):
                            payload = messaging_event['message']['quick_reply']['payload']

                            MessageSaver.store_message(sender_id, message_text=message_text, payload=payload)

                        else:
                            MessageSaver.store_message(sender_id, message_text=message_text)

                        return "ok", 200
                    elif messaging_event.get('postback'):
                        payload = messaging_event['postback']['payload']
                        message_text = messaging_event['postback']['title']

                        MessageSaver.store_message(sender_id, message_text=message_text, payload=payload)
                        return "ok", 200
    except:
        logging.exception('')

    log('nothing in data', None, 'app.py')
    return "ok", 200


@app.route('/promotion', methods=['GET'])
def redirect_to_chatbot():
    add_access_data(request.referrer)

    return redirect(
        'http://blooming-shore-23665.herokuapp.com/promotion/redirect')


@app.route('/promotion/redirect', methods=['GET'])
def redirect_to_promotion():
    return redirect('http://m.me/JullieChatbot')


if __name__ == '__main__':
    app.run(debug=True)
