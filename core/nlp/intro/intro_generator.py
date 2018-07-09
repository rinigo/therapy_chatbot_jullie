import logging
import models
from common.constant.intro_position import IntroPosition as IP
from common.constant.payloads import Payload
from common.constant.quick_replies import QuickReplies
from common.constant.user_status import UserStatus as US


class IntroGenerator(object):
    @classmethod
    def __start_introduction(cls, user):
        models.IntroPosition.register_new_intro(user)
        user.update_status(US.IN_INTRO.value)
        return cls.__create_greeting()

    @staticmethod
    def __create_greeting():
        try:
            responses = [
                "Hi! I am glad to meet you.",
            ]

            quick_replies_title = QuickReplies.greeting_title.value
            quick_replies = QuickReplies.greeting.value

            return responses, quick_replies_title, quick_replies, Payload.GREETING.value
        except:
            logging.exception('')
            return [], '', [], 'DEFAULT'

    @classmethod
    def generate_intro_responses(cls, message_dicts, user):
        try:
            message = message_dicts[0]['text']

            if user.status == US.GET_STARTED.value:
                return cls.__start_introduction(user)
            elif user.status == US.IN_INTRO.value:
                position = models.IntroPosition.find_position_by_user_id(user.id)

                if position == IP.GREETING.value:
                    return cls.__create_ask_suicide_illness(user.id, message)
                elif position == IP.ASK_SUICIDE_ILLNESS.value:
                    return cls.__create_have_suicide_illness_or_cct_1(user, message)
                elif position == IP.CCT_1.value:
                    return cls.__create_cct_2(user.id, message)
                elif position == IP.CCT_2.value:
                    return cls.__create_cct_3(user.id, message)
                elif position == IP.CCT_3.value:
                    return cls.__create_cct_4(user.id, message)
                elif position == IP.CCT_4.value:
                    return cls.__create_cct_5(user.id, message)
                elif position == IP.CCT_5.value:
                    return cls.__create_session_1(user.id, message)
                elif position == IP.SESSION_1.value:
                    return cls.__create_session_2(user.id, message)
                elif position == IP.SESSION_2.value:
                    return cls.__create_initial_regular_message(user, message)
            elif user.status == US.SUICIDE_ILLNESS.value:
                return cls.__handle_restart(user, message)
            else:
                print('Trying to make intro response_generator for users not in intro')
                return ["You know I'm always here for you."], '', [], 'DEFAULT'

        except Exception:
            logging.exception('Could not continue intro')
            return [], '', [], 'DEFAULT'

    @classmethod
    def __create_cct_1(cls, user_id, message):
        if message == QuickReplies.greeting.value[0]:
            responses = ["Client centered therapy is one approach to mental health"]
            quick_replies_title = QuickReplies.cct_1_title.value
            quick_replies = QuickReplies.cct_1.value
            payload = Payload.CCT_1.value

            models.IntroPosition.save_position(IP.CCT_1.value, user_id)
        else:
            responses = []
            quick_replies_title = QuickReplies.use_button_title.value
            quick_replies = QuickReplies.greeting.value
            payload = Payload.GREETING.value

        return responses, quick_replies_title, quick_replies, payload

    @classmethod
    def __create_cct_2(cls, user_id, message):
        responses = []

        if message == QuickReplies.cct_1.value[0]:
            quick_replies_title = QuickReplies.cct_2_title.value
            quick_replies = QuickReplies.cct_2.value
            payload = Payload.CCT_2.value

            models.IntroPosition.save_position(IP.CCT_2.value, user_id)
        else:
            quick_replies_title = QuickReplies.use_button_title.value
            quick_replies = QuickReplies.cct_1.value
            payload = Payload.CCT_1.value

        return responses, quick_replies_title, quick_replies, payload

    @classmethod
    def __create_cct_3(cls, user_id, message):
        responses = []
        if message == QuickReplies.cct_2.value[0]:
            responses = QuickReplies.responses_cct_3.value
            quick_replies_title = QuickReplies.cct_3_title.value
            quick_replies = QuickReplies.cct_3.value
            payload = Payload.CCT_3.value

            models.IntroPosition.save_position(IP.CCT_3.value, user_id)
        else:
            quick_replies_title = QuickReplies.use_button_title.value
            quick_replies = QuickReplies.cct_2.value
            payload = Payload.CCT_2.value

        return responses, quick_replies_title, quick_replies, payload

    @classmethod
    def __create_cct_4(cls, user_id, message):
        responses = []
        if message in QuickReplies.cct_3.value:
            quick_replies_title = QuickReplies.cct_4_title.value
            quick_replies = QuickReplies.cct_4.value
            payload = Payload.CCT_4.value

            models.IntroPosition.save_position(IP.CCT_4.value, user_id)
        else:
            quick_replies_title = QuickReplies.use_button_title.value
            quick_replies = QuickReplies.cct_3.value
            payload = Payload.CCT_3.value

        return responses, quick_replies_title, quick_replies, payload

    @classmethod
    def __create_cct_5(cls, user_id, message):
        responses = []
        if message in QuickReplies.cct_4.value:
            responses = QuickReplies.responses_cct_5.value
            quick_replies_title = QuickReplies.cct_5_title.value
            quick_replies = QuickReplies.cct_5.value
            payload = Payload.CCT_5.value

            models.IntroPosition.save_position(IP.CCT_5.value, user_id)
        else:
            quick_replies_title = QuickReplies.use_button_title.value
            quick_replies = QuickReplies.cct_4.value
            payload = Payload.CCT_4.value

        return responses, quick_replies_title, quick_replies, payload

    @classmethod
    def __create_session_1(cls, user_id, message):
        responses = []
        if message in QuickReplies.cct_5.value:
            responses = QuickReplies.responses_session_1.value
            quick_replies_title = QuickReplies.session_1_title.value
            quick_replies = QuickReplies.session_1.value
            payload = Payload.SESSION_1.value

            models.IntroPosition.save_position(IP.SESSION_1.value, user_id)
        else:
            quick_replies_title = QuickReplies.use_button_title.value
            quick_replies = QuickReplies.cct_5.value
            payload = Payload.CCT_5.value

        return responses, quick_replies_title, quick_replies, payload

    @classmethod
    def __create_session_2(cls, user_id, message):
        responses = []
        if message in QuickReplies.session_1.value:
            responses = QuickReplies.responses_session_2.value
            quick_replies_title = QuickReplies.session_2_title.value
            quick_replies = QuickReplies.session_2.value
            payload = Payload.SESSION_2.value

            models.IntroPosition.save_position(IP.SESSION_2.value, user_id)
        else:
            quick_replies_title = QuickReplies.use_button_title.value
            quick_replies = QuickReplies.session_1.value
            payload = Payload.SESSION_1.value

        return responses, quick_replies_title, quick_replies, payload

    @classmethod
    def __create_ask_suicide_illness(cls, user_id, message):
        responses = []
        if message in QuickReplies.greeting.value:
            responses = QuickReplies.responses_ask_suicide_illness.value
            quick_replies_title = QuickReplies.ask_suicide_illness_title.value
            quick_replies = QuickReplies.ask_suicide_illness.value
            payload = Payload.ASK_SUICIDE_ILLNESS.value

            models.IntroPosition.save_position(IP.ASK_SUICIDE_ILLNESS.value, user_id)
        else:
            quick_replies_title = QuickReplies.use_button_title.value
            quick_replies = QuickReplies.greeting.value
            payload = Payload.GREETING.value

        return responses, quick_replies_title, quick_replies, payload

    @classmethod
    def __create_have_suicide_illness_or_cct_1(cls, user, message):
        responses = []

        if message == QuickReplies.ask_suicide_illness.value[0]:
            responses = QuickReplies.responses_have_suicide_illness.value
            quick_replies_title = QuickReplies.have_suicidal_illness_title.value
            quick_replies = QuickReplies.have_suicidal_illness.value
            payload = Payload.HAVE_SUICIDE_ILLNESS.value

            models.IntroPosition.save_position(IP.HAVE_SUICIDE_ILLNESS.value, user.id)
            user.update_status(US.SUICIDE_ILLNESS.value)
        elif message == QuickReplies.ask_suicide_illness.value[1]:
            responses = QuickReplies.responses_cct_1.value
            quick_replies_title = QuickReplies.cct_1_title.value
            quick_replies = QuickReplies.cct_1.value
            payload = Payload.CCT_1.value

            models.IntroPosition.save_position(IP.CCT_1.value, user.id)
        else:
            quick_replies_title = QuickReplies.use_button_title.value
            quick_replies = QuickReplies.ask_suicide_illness.value
            payload = Payload.ASK_SUICIDE_ILLNESS.value

        return responses, quick_replies_title, quick_replies, payload

    @classmethod
    def __handle_restart(cls, user, message):
        responses = []
        if message in QuickReplies.have_suicidal_illness.value:
            responses = QuickReplies.responses_ask_suicide_illness.value
            quick_replies_title = QuickReplies.ask_suicide_illness_title.value
            quick_replies = QuickReplies.ask_suicide_illness.value
            payload = Payload.ASK_SUICIDE_ILLNESS.value

            models.IntroPosition.save_position(IP.ASK_SUICIDE_ILLNESS.value, user.id)
            user.update_status(US.IN_INTRO.value)
        else:
            quick_replies_title = QuickReplies.use_button_title.value
            quick_replies = QuickReplies.have_suicidal_illness.value
            payload = Payload.HAVE_SUICIDE_ILLNESS.value

        return responses, quick_replies_title, quick_replies, payload

    @classmethod
    def __create_initial_regular_message(cls, user, message):
        responses = []
        quick_replies_title = ""
        quick_replies = []
        payload = "DEFAULT"

        if message in QuickReplies.session_2.value:
            responses = QuickReplies.initial_regular_message.value

            models.IntroPosition.save_position(IP.DONE.value, user.id)
            user.update_status(US.FIRST_REGULAR_MESSAGE.value)
            models.Session.create_prepared_session(user.id)
        else:
            quick_replies_title = QuickReplies.use_button_title.value
            quick_replies = QuickReplies.session_2.value
            payload = Payload.SESSION_2.value

        return responses, quick_replies_title, quick_replies, payload
