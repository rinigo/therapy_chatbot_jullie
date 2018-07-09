import logging
from common.constant.admin_command import AdminCommand
from core.nlp.response_generator.factory.base_response_generator_factory import BaseResponseGeneratorFactory
from core.nlp.response_generator.product.admin.go_to_ask_mood_response_generator import GoToAskMoodResponseGenerator
from core.nlp.response_generator.product.admin.restart_introduction_response_generator import \
    RestartIntroductionResposneGenerator
from core.nlp.response_generator.product.admin.restart_session_response_generator import RestartSessionResponseGenerator


class AdminResponseGeneratorFactory(BaseResponseGeneratorFactory):
    @classmethod
    def create(cls, user, message, therapy_session):
        try:
            args = user, message, therapy_session

            word = [i['text'] for i in message.message_dicts][0]

            if word == AdminCommand.RESTART_INTRODUCTION.value:
                return RestartIntroductionResposneGenerator(*args)
            elif word == AdminCommand.RESTART_SESSION.value:
                return RestartSessionResponseGenerator(*args)
            elif word == AdminCommand.GO_TO_ASK_MOOD.value:
                return GoToAskMoodResponseGenerator(*args)
        except:
            logging.exception('')
