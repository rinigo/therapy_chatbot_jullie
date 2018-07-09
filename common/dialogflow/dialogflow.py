import logging
import os
from apiai import ApiAI
import json
from common.constant.intent_type import Intent
from common.word_format.word_formatter import WordFormatter


def request_to_apiai(df):
    try:
        message = WordFormatter.Df2Str(df)
        client_access_token = os.environ.get('client_access_token', None)
        session_id = os.environ.get('session_id', None)
        ai = ApiAI(client_access_token)
        request = ai.text_request()
        request.session_id = session_id
        request.query = message
        response = json.loads(request.getresponse().read().decode('utf-8'))

        try:
            if response is not None:
                if 'action' in response['result'].keys():
                    candidate = response['result']['action']

                    if Intent.has_value(candidate):
                        return Intent(candidate)
        except:
            logging.exception('')

        if is_haha_intent(message):
            return Intent.HAHA

        return Intent.NORMAL
    except:
        logging.exception('')
        return Intent.NORMAL


def is_haha_intent(message):
    try:
        return True if message in {'haha.', 'hahaha.', 'lol.'} else False
    except:
        logging.exception('')
        return False
