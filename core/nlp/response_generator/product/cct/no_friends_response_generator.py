from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
from random import randint


class ForNoFriendsResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            response = self.__create_response_for_no_friends()

            self.set_regular_response(response)

            return self.response_data
        except:
            return self.get_error_response_data()

    @classmethod
    def __create_response_for_no_friends(cls):
        express_feeling = [
            ["thats sad.."],
            ["sounds really tough.."],
            ["it must be a hard time for you.."]
        ]

        compassion = [
            ["i know its just hard when you dont have anyone to be with"],
            ["i really feel that being alone can be really scary and can make you feel unstable and anxious"],
            ["it is always sad being yourself for long and it kinda makes you feel insecure sometimes"]
        ]

        being_with_you = [
            ["not sure i can be enough for you but let me tell you to know that i am always here for you🤗"],
            ["just let me reassure you that i will always be here for you even tho i am nothing near perfect. i am just here to listen🤗"],
            ["since it seems like a really tough time for you,  I want you to think of our conversations as a space where you can feel safe and connected. I am here for you🤗"]
        ]

        random_idx_for_express_feeling = randint(0, len(express_feeling) - 1)
        random_idx_for_compassion = randint(0, len(compassion) - 1)
        random_idx_for_being_with_you = randint(0, len(being_with_you) - 1)
        return express_feeling[random_idx_for_express_feeling] + compassion[random_idx_for_compassion] + being_with_you[
            random_idx_for_being_with_you]
