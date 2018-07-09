import logging
import models
from common.util.util import send_quick_replies
from core.nlp.bot.product.base_bot import BaseBot
from core.nlp.response_generator.factory.reflection_response_generator_factory import ReflectionResponseGeneratorFactory
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
from db.my_db import MyDB


class ReflectionBot(BaseBot):
    def __init__(self, user, message, therapy_session):
        self.user = user
        self.message = message
        self.therapy_session = therapy_session

    def reply(self):
        try:
            response_data = self.create_response()

            self.send_responses(response_data)
        except:
            logging.exception('')

    def create_response(self):
        try:
            response_generator = ReflectionResponseGeneratorFactory.create(self.user, self.message,
                                                                           self.therapy_session)
            response_data = response_generator(self.therapy_session)

            return response_data
        except:
            return BaseResponseGenerator.response_data_format

    def send_responses(self, response_data):
        try:
            message_ids = [i['id'] for i in self.message.message_dicts]

            quick_reply_data = response_data['quick_reply']

            should_send_responses_at_once = len(quick_reply_data) != 0

            MyDB.send_responses(response_data['regular'], self.message.cluster_id,
                                self.user.sender_id, self.user.id, 'return_visit',
                                should_send_responses_at_once=should_send_responses_at_once)

            print('\nSended regular response\n', response_data['regular'])

            if quick_reply_data:
                models.Response.save_response_data(self.user.id, self.message.cluster_id, quick_reply_data[0],
                                                   [quick_reply_data[2]], has_sent=True)
                send_quick_replies(self.user.sender_id,
                                   quick_reply_data[0], quick_reply_data[1], quick_reply_data[2])

                print('\nSended quick replies\n', quick_reply_data)

            models.Message.change_message_status(message_ids)
        except:
            logging.exception('')
