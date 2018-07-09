import logging
from pprint import pprint
from typing import Dict, List
import models
from common.constant.session_status import SessionStatus
from common.constant.user_status import UserStatus
from common.util.util import send_typing_on, send_quick_replies
from core.models.message import Message
from core.models.therapy_session import TherapySession
from core.models.user import User
from core.nlp.bot.product.base_bot import BaseBot
from core.nlp.message_preprocessor import MessagePreprocessor
from core.nlp.message_type_checker import MessageTypeChecker
from core.nlp.response_generator.factory.cct_response_generator_factory import CCTResponseGeneratorFactory
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
from db.my_db import MyDB
from models import UsersFeeling
from random import shuffle


class CCTBot(BaseBot):
    def __init__(self, user: User, message: Message, therapy_session: TherapySession):
        self.user = user
        self.message = message
        self.therapy_session = therapy_session

    def reply(self):
        try:
            if self.therapy_session.status == SessionStatus.prepared.value:
                self.therapy_session.activate()

            send_typing_on(self.user.sender_id)

            self.message = self.preprocess_message()

            send_typing_on(self.user.sender_id)

            UsersFeeling.save_feelings(self.message.text_kw_df, self.user.id)

            message_types = self.analyze_message_type()

            send_typing_on(self.user.sender_id)

            response_data = self.create_response(message_types)

            send_typing_on(self.user.sender_id)

            self.send_responses(response_data, message_types)
            print("\nBot finished sending responses")
        except:
            logging.exception('')
            print('\n*********************** Bot couldnt make responses ***********************')

    def preprocess_message(self):
        try:
            preprocessor = MessagePreprocessor()
            processed_message = preprocessor(self.message, self.user)

            print("\n---------------- self.message ----------------",
                  "\nOriginal DF\n", processed_message.original_df,
                  "\n\ntext_df\n", processed_message.text_df,
                  "\n\ntext_kw_df\n", processed_message.text_kw_df,
                  '\n\nintent_list\n', processed_message.intent_list,
                  '\n\nsentiment_score_df\n', processed_message.sentiment_score_df,
                  '\n----------------------------------------------')

            return processed_message
        except:
            logging.exception('')

    def analyze_message_type(self):
        try:
            msg_type_checker = MessageTypeChecker(self.user, self.message)
            message_types = msg_type_checker()

            print('\nmessage_types\n', message_types)

            return message_types
        except:
            logging.exception('')
            return []

    def create_response(self, message_types):
        response_data = BaseResponseGenerator.response_data_format

        try:
            for t in message_types:
                response_generator = CCTResponseGeneratorFactory.create(self.user, self.message, t)
                r = response_generator()

                response_data['regular'] += r['regular']
                response_data['quick_reply'] = r['quick_reply']

            print('\nresponse data')
            pprint(response_data)

            return response_data
        except:
            logging.exception('')
            error_options = [["i see.."], ["okay.."], ["right.."]]
            shuffle(error_options)
            response_data['regular'] = error_options[0]
            return response_data

    def send_responses(self, response_data: Dict[str, List[str]], message_types: List[str]):
        try:
            message_ids = [i['id'] for i in self.message.message_dicts]

            is_session_active = self.therapy_session.status == SessionStatus.active.value
            exists_new_message = models.Message.has_user_sent_new_message(self.user.id, message_ids)
            is_user_suicidal = self.user.status == UserStatus.SUICIDE_IN_SESSION.value

            if not is_user_suicidal and is_session_active and exists_new_message:
                self.__restart_msg_processing(message_ids)
                return

            quick_reply_data = response_data['quick_reply']

            should_send_responses_at_once = len(quick_reply_data) != 0
            MyDB.send_responses(response_data['regular'], self.message.cluster_id, self.user.sender_id,
                                self.user.id, message_types,
                                should_send_responses_at_once=should_send_responses_at_once)

            print('\nSended regular response\n', response_data['regular'])

            if quick_reply_data:
                models.Response.save_response_data(self.user.id, self.message.cluster_id, quick_reply_data[0],
                                                   [quick_reply_data[2]], has_sent=True)

                send_quick_replies(self.user.sender_id, quick_reply_data[0], quick_reply_data[1],
                                   quick_reply_data[2])
                print('\nSended quick replies\n', quick_reply_data)
        except:
            logging.exception('')

    def __restart_msg_processing(self, message_ids):
        try:
            print("\n------ Restart message processing because of new messaage during the process -------\n")

            models.Message.change_current_and_new_message_status(message_ids, self.user.id)
        except:
            logging.exception('')
