import random

from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class CallMeNamesResponseGenerator(BaseResponseGenerator):
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
                    "That's so annoying..."
                ],
                [
                    "That's so stressful right?"
                ],
                [
                    "That's so tough having someone like that..."
                ]
            ]

            responses = random.choice(options)

            self.set_regular_response(responses)

            return self.response_data
        except:
            return self.get_error_response_data()
