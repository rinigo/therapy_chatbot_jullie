import models
from common.constant.quick_replies import QuickReplies
from common.constant.session_status import SessionStatus
from core.models.therapy_session import TherapySession
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class AskMoodResponseGenerator(BaseResponseGenerator):
    def __call__(self, therapy_session: TherapySession):
        try:
            models.Session.save_comment_end(therapy_session.id, self.message)

            therapy_session.change_status(SessionStatus.asking_mood.value)

            self.response_data = self.__create_response_for_ask_mood()

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_response_for_ask_mood(self):
        try:
            responses = ['Thank you.']

            self.set_regular_response(responses)

            quick_replies_title = QuickReplies.ask_mood_end_title.value
            quick_replies = QuickReplies.ask_mood_end_options.value
            payload = 'ask_mood'

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()
