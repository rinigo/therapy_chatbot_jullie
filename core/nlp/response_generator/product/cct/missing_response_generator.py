import random

from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class MissingResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            self.response_data = self.__create_response()

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_response(self):
        try:
            options = [
                [
                    "That must feel very sad.",
                    "Not having the one you used to have is so tough",
                    "But here I am to help you feel better :)"
                ],
                [
                    "Missing is really tough feeling.",
                    "I don't know if you feel comfortable but you always have me here so no worry :)"
                ],
                [
                    "Was so important for you right...",
                    "Though you feel a pit in your mind, I hope talking with me makes you feel any better"
                ]
            ]

            response = random.choice(options)

            self.set_regular_response(response)

            return self.response_data
        except:
            return self.get_error_response_data()
