import models
from common.constant.session_status import SessionStatus
from common.constant.string_constant import StringConstant
from core.models.therapy_session import TherapySession
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class AskNewSessionResponseGenerator(BaseResponseGenerator):
    def __call__(self, therapy_session: TherapySession):
        try:
            models.Session.create_new_session(self.user.id)
            models.Session.update_latest_session_status(SessionStatus.asking_new.value, self.user.id)

            responses = StringConstant.ask_session_start_text_retention.value

            self.set_regular_response(responses)

            quick_replies_title = StringConstant.ask_session_start_quick_replies_title.value
            quick_replies = StringConstant.ask_session_start_quick_replies.value
            payload = 'ask_new_session'

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()
