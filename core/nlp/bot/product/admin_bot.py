import logging
import models
from core.nlp.bot.product.base_bot import BaseBot
from core.nlp.response_generator.factory.admin_response_generator_factory import AdminResponseGeneratorFactory
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
from db.my_db import MyDB


class AdminBot(BaseBot):
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
            response_generator = AdminResponseGeneratorFactory.create(self.user, self.message, self.therapy_session)
            response_data = response_generator()

            return response_data
        except:
            logging.exception('')
            return BaseResponseGenerator.response_data_format

    def send_responses(self, response_data):
        try:
            message_ids = [i['id'] for i in self.message.message_dicts]

            MyDB.send_responses(response_data['regular'], self.message.cluster_id, self.user.sender_id,
                                self.user.id, 'admin', should_send_responses_at_once=True)

            print('\nSended regular response\n', response_data['regular'])

            models.Message.change_message_status(message_ids)
        except:
            logging.exception('')
