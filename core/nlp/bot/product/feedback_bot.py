import logging
import models
from common.constant.message_type import MessageType
from common.constant.session_status import SessionStatus
from core.nlp.bot.product.base_bot import BaseBot
from core.nlp.response_generator.factory.cct_response_generator_factory import CCTResponseGeneratorFactory
from db.my_db import MyDB


class FeedbackBot(BaseBot):
    def reply(self):
        pass

    def find_inactivated_users(self):
        try:
            inactivated_users = models.User.find_inactivated_user_ids()

            return inactivated_users
        except:
            logging.exception('')
            return []

    def ask_feed_back(self, users: list):
        try:
            if not users:
                return

            response_data = self.create_response(users[0])

            for user_id in users:
                self.send_responses(response_data, user_id)

                self.change_session_status(user_id)

                print('\n[ASKED COMMENT] User ' + str(user_id))
        except:
            logging.exception('')

    def create_response(self, user):
        try:
            response_generator = CCTResponseGeneratorFactory.create(user, None, MessageType.ASK_FEED_BACK.value)
            response_data = response_generator()

            return response_data
        except:
            logging.exception('')
            return []

    def send_responses(self, response_data, user_id):
        try:
            sender_id = models.User.find_sender_id_by_id(user_id)
            MyDB.send_responses(response_data['regular'], None, sender_id,
                                user_id, MessageType.ASK_FEED_BACK.value, should_send_responses_at_once=True)
        except:
            logging.exception('')

    def change_session_status(self, user_id):
        try:
            latest_session = models.Session.find_latest_session_data(user_id)
            models.Session.update_status(latest_session['id'], SessionStatus.asking_comment.value)
        except:
            logging.exception('')
