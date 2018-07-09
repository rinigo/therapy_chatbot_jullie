import models
from common.constant.payloads import Payload
from common.constant.quick_replies import QuickReplies
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
from common.constant.user_status import UserStatus as US
from common.constant.intro_position import IntroPosition as IP


class IntroResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            answer = [i['text'] for i in self.message.message_dicts][0]

            print('\nuser answer\n', answer)

            if self.user.status == US.GET_STARTED.value:
                return self.__start_introduction()
            elif self.user.status == US.INTRO.value:
                position = models.IntroPosition.find_position_by_user_id(self.user.id)
                print('\nIntro position\n', position)

                if position == IP.GREETING.value:
                    return self.__create_ask_suicide_illness(answer)
                elif position == IP.ASK_SUICIDE_ILLNESS.value:
                    return self.__create_have_suicide_illness_or_cct_1(answer)
                elif position == IP.CCT_1.value:
                    return self.__create_cct_2(answer)
                elif position == IP.CCT_2.value:
                    return self.__create_cct_3(answer)
                elif position == IP.CCT_3.value:
                    return self.__create_cct_4(answer)
                elif position == IP.CCT_4.value:
                    return self.__create_cct_5(answer)
                elif position == IP.CCT_5.value:
                    return self.__create_session_1(answer)
                elif position == IP.SESSION_1.value:
                    return self.__create_session_2(answer)
                elif position == IP.SESSION_2.value:
                    return self.__create_initial_regular_message(answer)
            elif self.user.status == US.SUICIDE_ILLNESS_INTRO.value:
                return self.__handle_restart(answer)
            else:
                return self.__create_non_intro_response()
        except:
            return self.get_error_response_data()

    def __start_introduction(self):
        models.IntroPosition.register_new_intro(self.user)
        self.user.update_status(US.INTRO.value)
        return self.__create_greeting()

    def __create_greeting(self):
        try:
            responses = [
                "Hi! I am glad to meet you.",
            ]

            quick_replies_title = QuickReplies.greeting_title.value
            quick_replies = QuickReplies.greeting.value
            payload = Payload.GREETING.value
            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_regular_response(responses)
            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_cct_1(self, answer):
        try:
            if answer == QuickReplies.greeting.value[0]:
                responses = ["Client centered therapy is one approach to mental health"]
                quick_replies_title = QuickReplies.cct_1_title.value
                quick_replies = QuickReplies.cct_1.value
                payload = Payload.CCT_1.value

                models.IntroPosition.save_position(IP.CCT_1.value, self.user.id)
            else:
                responses = []
                quick_replies_title = QuickReplies.use_button_title.value
                quick_replies = QuickReplies.greeting.value
                payload = Payload.GREETING.value

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_regular_response(responses)
            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_cct_2(self, answer):
        try:
            responses = []

            if answer == QuickReplies.cct_1.value[0]:
                quick_replies_title = QuickReplies.cct_2_title.value
                quick_replies = QuickReplies.cct_2.value
                payload = Payload.CCT_2.value

                models.IntroPosition.save_position(IP.CCT_2.value, self.user.id)
            else:
                quick_replies_title = QuickReplies.use_button_title.value
                quick_replies = QuickReplies.cct_1.value
                payload = Payload.CCT_1.value

            quick_reply_data = [quick_replies_title, quick_replies, payload]


            self.set_regular_response(responses)
            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_cct_3(self, answer):
        try:
            responses = []
            if answer == QuickReplies.cct_2.value[0]:
                responses = QuickReplies.responses_cct_3.value
                quick_replies_title = QuickReplies.cct_3_title.value
                quick_replies = QuickReplies.cct_3.value
                payload = Payload.CCT_3.value

                models.IntroPosition.save_position(IP.CCT_3.value, self.user.id)
            else:
                quick_replies_title = QuickReplies.use_button_title.value
                quick_replies = QuickReplies.cct_2.value
                payload = Payload.CCT_2.value

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_regular_response(responses)
            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_cct_4(self, answer):
        try:
            responses = []
            if answer in QuickReplies.cct_3.value:
                quick_replies_title = QuickReplies.cct_4_title.value
                quick_replies = QuickReplies.cct_4.value
                payload = Payload.CCT_4.value

                models.IntroPosition.save_position(IP.CCT_4.value, self.user.id)
            else:
                quick_replies_title = QuickReplies.use_button_title.value
                quick_replies = QuickReplies.cct_3.value
                payload = Payload.CCT_3.value

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_regular_response(responses)
            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_cct_5(self, answer):
        try:
            responses = []
            if answer in QuickReplies.cct_4.value:
                responses = QuickReplies.responses_cct_5.value
                quick_replies_title = QuickReplies.cct_5_title.value
                quick_replies = QuickReplies.cct_5.value
                payload = Payload.CCT_5.value

                models.IntroPosition.save_position(IP.CCT_5.value, self.user.id)
            else:
                quick_replies_title = QuickReplies.use_button_title.value
                quick_replies = QuickReplies.cct_4.value
                payload = Payload.CCT_4.value

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_regular_response(responses)
            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_session_1(self, answer):
        try:
            responses = []
            if answer in QuickReplies.cct_5.value:
                responses = QuickReplies.responses_session_1.value
                quick_replies_title = QuickReplies.session_1_title.value
                quick_replies = QuickReplies.session_1.value
                payload = Payload.SESSION_1.value

                models.IntroPosition.save_position(IP.SESSION_1.value, self.user.id)
            else:
                quick_replies_title = QuickReplies.use_button_title.value
                quick_replies = QuickReplies.cct_5.value
                payload = Payload.CCT_5.value

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_regular_response(responses)
            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_session_2(self, answer):
        try:
            responses = []
            if answer in QuickReplies.session_1.value:
                responses = QuickReplies.responses_session_2.value
                quick_replies_title = QuickReplies.session_2_title.value
                quick_replies = QuickReplies.session_2.value
                payload = Payload.SESSION_2.value

                models.IntroPosition.save_position(IP.SESSION_2.value, self.user.id)
            else:
                quick_replies_title = QuickReplies.use_button_title.value
                quick_replies = QuickReplies.session_1.value
                payload = Payload.SESSION_1.value

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_regular_response(responses)
            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_ask_suicide_illness(self, answer):
        try:
            responses = []
            if answer in QuickReplies.greeting.value:
                responses = QuickReplies.responses_ask_suicide_illness.value
                quick_replies_title = QuickReplies.ask_suicide_illness_title.value
                quick_replies = QuickReplies.ask_suicide_illness.value
                payload = Payload.ASK_SUICIDE_ILLNESS.value

                models.IntroPosition.save_position(IP.ASK_SUICIDE_ILLNESS.value, self.user.id)
            else:
                quick_replies_title = QuickReplies.use_button_title.value
                quick_replies = QuickReplies.greeting.value
                payload = Payload.GREETING.value

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_regular_response(responses)
            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_have_suicide_illness_or_cct_1(self, answer):
        try:
            responses = []

            if answer == QuickReplies.ask_suicide_illness.value[0]:
                responses = QuickReplies.responses_have_suicide_illness.value
                quick_replies_title = QuickReplies.have_suicidal_illness_title.value
                quick_replies = QuickReplies.have_suicidal_illness.value
                payload = Payload.HAVE_SUICIDE_ILLNESS.value

                models.IntroPosition.save_position(IP.HAVE_SUICIDE_ILLNESS.value, self.user.id)
                self.user.update_status(US.SUICIDE_ILLNESS_INTRO.value)
            elif answer == QuickReplies.ask_suicide_illness.value[1]:
                responses = QuickReplies.responses_cct_1.value
                quick_replies_title = QuickReplies.cct_1_title.value
                quick_replies = QuickReplies.cct_1.value
                payload = Payload.CCT_1.value

                models.IntroPosition.save_position(IP.CCT_1.value, self.user.id)
            else:
                quick_replies_title = QuickReplies.use_button_title.value
                quick_replies = QuickReplies.ask_suicide_illness.value
                payload = Payload.ASK_SUICIDE_ILLNESS.value

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_regular_response(responses)
            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()

    def __handle_restart(self, answer):
        try:
            responses = []
            if answer in QuickReplies.have_suicidal_illness.value:
                responses = QuickReplies.responses_ask_suicide_illness.value
                quick_replies_title = QuickReplies.ask_suicide_illness_title.value
                quick_replies = QuickReplies.ask_suicide_illness.value
                payload = Payload.ASK_SUICIDE_ILLNESS.value

                models.IntroPosition.save_position(IP.ASK_SUICIDE_ILLNESS.value, self.user.id)
                self.user.update_status(US.INTRO.value)
            else:
                quick_replies_title = QuickReplies.use_button_title.value
                quick_replies = QuickReplies.have_suicidal_illness.value
                payload = Payload.HAVE_SUICIDE_ILLNESS.value

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_regular_response(responses)
            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_initial_regular_message(self, answer):
        try:
            responses = []
            quick_replies_title = ""
            quick_replies = []
            payload = "DEFAULT"

            if answer in QuickReplies.session_2.value:
                responses = QuickReplies.initial_regular_message.value

                models.IntroPosition.save_position(IP.DONE.value, self.user.id)
                self.user.update_status(US.REGULAR.value)
                models.Session.create_prepared_session(self.user.id)
            else:
                quick_replies_title = QuickReplies.use_button_title.value
                quick_replies = QuickReplies.session_2.value
                payload = Payload.SESSION_2.value

            quick_reply_data = [quick_replies_title, quick_replies, payload]

            self.set_regular_response(responses)
            self.set_quick_reply(quick_reply_data)

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_non_intro_response(self):
        try:
            print('Trying to make intro response_generator for users not in intro')

            self.set_regular_response("You know I'm always here for you.")

            return self.response_data
        except:
            return self.get_error_response_data()
