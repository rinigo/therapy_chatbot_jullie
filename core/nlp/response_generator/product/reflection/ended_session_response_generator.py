from common.constant.string_constant import StringConstant
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class EndedSessionResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            self.response_data = self.create_interval_response()

            return self.response_data
        except:
            return self.get_error_response_data()

    def create_interval_response(self):
        try:
            print("\n[USER IN INTERVAL] User " + str(self.user.id))

            responses = StringConstant.interval_responses.value

            self.set_regular_response(responses)

            return self.response_data
        except:
            return self.get_error_response_data()
