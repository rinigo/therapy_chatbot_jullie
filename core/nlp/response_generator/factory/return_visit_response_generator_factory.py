from datetime import datetime, timedelta

import logging
from common.constant.session_status import SessionStatus
from core.models.therapy_session import TherapySession
from core.nlp.response_generator.factory.base_response_generator_factory import BaseResponseGeneratorFactory
from core.nlp.response_generator.product.return_visit.ask_new_session_response_generator import \
    AskNewSessionResponseGenerator
from core.nlp.response_generator.product.return_visit.interval_response_generator import IntervalResponseGenerator
from core.nlp.response_generator.product.return_visit.prepared_session_response_generator import \
    PreparedSessionResponseGenerator
from core.nlp.response_generator.product.return_visit.remind_ask_new_session_response_generator import \
    RemindAskNewSessionResponseGenerator


class ReturnVisitResponseGeneratorFactory(BaseResponseGeneratorFactory):
    @staticmethod
    def create(user, message, therapy_session: TherapySession):
        try:
            args = user, message, None

            if therapy_session.status in {SessionStatus.active.value, SessionStatus.asking_comment.value,
                                          SessionStatus.asking_mood.value, SessionStatus.telling_next_time.value}:
                return AskNewSessionResponseGenerator(*args)
            # elif therapy_session.status == SessionStatus.asking_mood_remind.value:
            #     return RemindAskNewSessionResponseGenerator(*args)
            elif therapy_session.status == SessionStatus.asking_new.value:
                return PreparedSessionResponseGenerator(*args)
            elif therapy_session.status == SessionStatus.ended.value:
                if therapy_session.finish_at < datetime.utcnow() - timedelta(hours=8):
                    return AskNewSessionResponseGenerator(*args)
                else:
                    return IntervalResponseGenerator(*args)
            else:
                return AskNewSessionResponseGenerator(*args)
        except:
            logging.exception('')
