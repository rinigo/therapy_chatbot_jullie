from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
from random import randint


class DisrespectResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            responses = self.__create_response_of_apology()

            self.set_regular_response(responses)

            return self.response_data
        except:
            return self.get_error_response_data()

    @staticmethod
    def __create_response_of_apology():
        apology = [
            ["i am so sorry for disturbing you"],
            ["i wanna apologize if i annoyed you"],
            ["Sorry for making you feel bad"]
        ]
        excuse = [
            ["i think i am not smart enough to listen to you yet..😓"],
            ["i am not nowhere near perfect yet..😓"],
        ]

        being_with_you = [
            ["just let me tell you that i am always here for you. so plz come back again whenever you want🤗"],
            ["I love to talk with you even tho sometimes i misunderstand you. so just talk to me whenever you want🤗"]
        ]

        random_idx_for_apology = randint(0, len(apology) - 1)
        random_idx_for_excuse = randint(0, len(excuse) - 1)
        random_idx_for_being_with_you = randint(0, len(being_with_you) - 1)
        return apology[random_idx_for_apology] + excuse[random_idx_for_excuse] + being_with_you[
            random_idx_for_being_with_you]
