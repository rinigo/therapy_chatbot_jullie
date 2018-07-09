import random

from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class AnxiousResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            self.response_data = self.create_anxious_response()

            return self.response_data
        except:
            return self.get_error_response_data()

    def create_anxious_response(self):
        try:
            options = [
                [
                    "I am sorry to hear that you are going through this",
                    "Although people don't understand it and may be unsympathetic, you can talk to me :)"
                ],
                [
                    "I know it can even feel like things are just always overwhelming and it's so hard",
                    "but even when you feel no one understands, try to remember that I'm here to listen to you"
                ]
            ]
            responses = random.choice(options)

            self.set_regular_response(responses)

            return self.response_data
        except:
            return self.get_error_response_data()
