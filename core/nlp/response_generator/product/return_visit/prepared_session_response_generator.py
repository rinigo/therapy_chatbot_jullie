from datetime import datetime, timedelta
import logging
import models
from common.constant.quick_replies import QuickReplies
from common.constant.session_status import SessionStatus
from common.constant.string_constant import StringConstant
from core.models.therapy_session import TherapySession
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class PreparedSessionResponseGenerator(BaseResponseGenerator):
    def __call__(self, therapy_session):
        try:
            answer = [i['text'] for i in self.message.message_dicts][0]

            if answer == StringConstant.ask_session_start_quick_replies.value[0]:
                therapy_session.prepare()
                self.response_data = self.__create_response_for_prepare()
            elif answer == StringConstant.ask_session_start_quick_replies.value[1]:
                self.__handle_leaving_user_session(therapy_session)
                self.response_data = self.__create_response_for_leaving()
            else:
                self.response_data = self.__create_response_for_use_button()

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_response_for_prepare(self):
        try:
            responses = [
                "Sure!",
                "Tell me what you have in your mind :)"
            ]

            self.set_regular_response(responses)

            return self.response_data
        except:
            return self.get_error_response_data()

    def __handle_leaving_user_session(self, therapy_session):
        try:
            therapy_session.change_status(SessionStatus.ended.value)

            new_finish_at = datetime.utcnow() - timedelta(hours=TherapySession.interval_after_session)
            models.Session.update_finish_at(therapy_session.id, new_finish_at)
        except:
            logging.exception('')

    def __create_response_for_leaving(self):
        try:
            responses = StringConstant.interval_responses.value

            self.set_regular_response(responses)

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_response_for_use_button(self):
        try:
            quick_replies_title = QuickReplies.use_button_title.value
            quick_replies = StringConstant.ask_session_start_quick_replies.value
            payload = 'use_button'

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()
