from datetime import datetime, timedelta
import logging
import models
from common.constant.quick_replies import QuickReplies
from common.constant.session_status import SessionStatus
from core.models.therapy_session import TherapySession
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class FinishedSessionResponseGenerator(BaseResponseGenerator):
    def __call__(self, therapy_session: TherapySession):
        try:
            answer = [i['text'] for i in self.message.message_dicts][0]

            if answer in QuickReplies.ask_mood_end_options.value:
                models.Session.save_mood_end(self.user.id, answer)
                therapy_session.change_status(SessionStatus.ended.value)

                self.response_data = self.__create_response_for_telling_next_time()
            else:
                self.response_data = self.__create_response_for_use_button()

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_response_for_telling_next_time(self):
        try:
            hours_to_wait, minutes_to_wait = self.calculate_remaining_interval_time()

            responses = [
                "Thank you for telling me about your mood😝",
                "After every session, you need break time to re-think your problem.",
                "You can come here anytime after " + str(hours_to_wait) + " hours and " + str(
                    minutes_to_wait) + " minutes.",
                "That might make you feel a little nervous, but I'm sure you can deal with your concerns."
                "So I hope this session helps you in some way.",
                "See you later🤗"
            ]

            self.set_regular_response(responses)

            return self.response_data
        except:
            return self.get_error_response_data()

    def calculate_remaining_interval_time(self):
        try:
            session_end_time = models.Session.find_latest_session_finish_at(self.user.id)

            time_to_wait = session_end_time + timedelta(hours=8) - datetime.utcnow()
            hours_to_wait = time_to_wait.seconds // 60 // 60
            minutes_to_wait = time_to_wait.seconds // 60 % 60

            return hours_to_wait, minutes_to_wait
        except:
            logging.exception('')
            return 0, 0

    def __create_response_for_use_button(self):
        try:
            quick_replies_title = QuickReplies.use_button_title.value
            quick_replies = QuickReplies.ask_mood_end_options.value
            payload = 'use_button_asking_mood'

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()
