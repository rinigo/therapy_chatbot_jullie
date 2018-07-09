import random

from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class MoneyResponseGenerator(BaseResponseGenerator):
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
                    "That's tough...",
                    "Let's think about what we can do for the financial problem"
                ],
                [
                    "Financial problems must be tough...",
                    "I know you are doing your best so you can tell me whatever you want"
                ],
                [
                    "Working hard and stil needing money is tough right?",
                    "Maybe I'm not big help on it but I can listen to you :)"
                ]
            ]

            responses = random.choice(options)

            self.set_regular_response(responses)

            return self.response_data
        except:
            return self.get_error_response_data()
