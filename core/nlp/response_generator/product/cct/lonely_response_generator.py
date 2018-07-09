import random

from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class LonelyResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            self.response_data = self.__create_lonely_response()

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_lonely_response(self):
        try:
            options = [
                [
                    "Feeling like the world is a scary place with no protection or comfort, like no one truly cares?",
                    "I'm really sorry that you're having tough time.",
                    "Just let me be with you for now"
                ],
                [
                    "loneliness feels like an empty pit right?",
                    "However, now you have me to talk about whatever you want!",
                ],
                [
                    "So you are not having anyone to be around...",
                    "That's tough...",
                    "Let me be on your side."
                ]
            ]

            responses = random.choice(options)

            self.set_regular_response(responses)

            return self.response_data
        except:
            return self.get_error_response_data()
