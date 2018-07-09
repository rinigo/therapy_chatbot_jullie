import logging
import models
from common.constant.quick_replies import QuickReplies
from common.constant.session_status import SessionStatus
from common.constant.string_constant import StringConstant
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class RemindAskNewSessionResponseGenerator(BaseResponseGenerator):
    def __call__(self, therapy_session):
        try:
            answer = [i['text'] for i in self.message.message_dicts][0]

            if answer in StringConstant.remind_quick_replies.value:
                self.__handle_mood(answer, therapy_session)

                self.response_data = self.__create_response_for_asking_new_session()
            else:
                self.response_data = self.__create_response_for_use_button()

            return self.response_data
        except:
            return self.get_error_response_data()

    def __handle_mood(self, answer, therapy_session):
        try:
            if answer in StringConstant.remind_quick_replies.value:
                models.Remind.register_remind_mood(answer, self.user.id)
                therapy_session.change_status(SessionStatus.asking_new.value)
        except:
            logging.exception('')

    def __create_response_for_asking_new_session(self):
        try:
            responses = StringConstant.ask_session_start_text.value

            self.set_regular_response(responses)

            quick_replies_title = StringConstant.ask_session_start_quick_replies_title
            quick_replies = StringConstant.ask_session_start_quick_replies.value
            payload = 'ask_new_session'

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_quick_reply(quick_reply_data)

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
