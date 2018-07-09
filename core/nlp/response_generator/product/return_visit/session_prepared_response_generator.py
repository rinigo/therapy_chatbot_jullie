from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class SessionPreparedResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            responses = [
                "Sure!",
                "Tell me what you have in your mind :)"
            ]

            self.set_regular_response(responses)

            return self.response_data
        except:
            return self.get_error_response_data()
