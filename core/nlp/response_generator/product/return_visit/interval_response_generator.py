from common.constant.string_constant import StringConstant
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class IntervalResponseGenerator(BaseResponseGenerator):
    def __call__(self, *args):
        try:
            responses = StringConstant.interval_responses.value

            self.set_regular_response(responses)

            return self.response_data
        except:
            return self.get_error_response_data()
