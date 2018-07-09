import logging
from common.constant.session_status import SessionStatus
from core.models.message import Message
from core.models.therapy_session import TherapySession
from core.models.user import User
from core.nlp.response_generator.factory.base_response_generator_factory import BaseResponseGeneratorFactory
from core.nlp.response_generator.product.reflection.ask_comment_response_generator import AskCommentResponseGenerator
from core.nlp.response_generator.product.reflection.ask_mood_response_generator import AskMoodResponseGenerator
from core.nlp.response_generator.product.reflection.finished_session_response_generator import \
    FinishedSessionResponseGenerator


class ReflectionResponseGeneratorFactory(BaseResponseGeneratorFactory):
    @classmethod
    def create(cls, user: User, message: Message, therapy_session: TherapySession):
        try:
            args = user, message, None

            if therapy_session.status == SessionStatus.active.value:
                return AskCommentResponseGenerator(*args)
            elif therapy_session.status == SessionStatus.asking_comment.value:
                return AskMoodResponseGenerator(*args)
            elif therapy_session.status == SessionStatus.asking_mood.value:
                return FinishedSessionResponseGenerator(*args)
            # elif therapy_session.status == SessionStatus.asking_mood_remind.value:
            #     return RemindAskingMoodResponseGenerator(*args)

        except:
            logging.exception('')
