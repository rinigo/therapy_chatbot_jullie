import logging
import re
from datetime import datetime, timedelta
from nltk import sent_tokenize
import models


class MessageSaver:
    @classmethod
    def store_message(cls, sender_id, message_text, payload=None):
        try:
            models.User.register_user(sender_id)
            user_id = models.User.find_by_sender_id(sender_id)

            if payload is None:
                message_text = cls.__format_raw_message_text(message_text)

                # save sent_tokenized messages in db.
                # no other operations here because delay in returning 'ok', 200 cause problem to webhook
                payload = ''

            cls.__save_message_to_db(user_id, message_text, payload=payload)
        except:
            logging.exception('')

    @staticmethod
    def __save_message_to_db(user_id, message, payload=''):
        try:
            first_name = models.User.find_first_name_by_id(user_id)
            if first_name in {'Yuya', 'Rintaro'}:
                created_at = datetime.utcnow() - timedelta(seconds=20)
            else:
                created_at = datetime.utcnow()

            print('saving messages',  message)

            for sentence in sent_tokenize(message):
                models.Message.save_message(user_id, created_at, sentence, payload)
        except:
            logging.exception('')

    @staticmethod
    def __format_raw_message_text(message_text):
        try:
            # add space after '.' so that messages can be tokenized correctly
            message_text = re.sub(r'\.([a-zA-Z])', r'. \1', message_text)

            message_text = message_text.replace('.\n', '. ')

            # replace \n to '.'
            message_text = message_text.replace('\n', '. ')

            message_text = re.sub(r'\.\s\.', '.', message_text)

            message_text = re.sub(r'\?{2,}', "?", message_text)
            message_text = re.sub(r'\.{2,}', ".", message_text)
            message_text = re.sub(r'!{2,}', "!", message_text)

            return message_text
        except:
            logging.exception('')
