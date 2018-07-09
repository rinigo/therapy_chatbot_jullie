from common.constant.string_constant import StringConstant
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class AskFeedbackResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            response = StringConstant.ask_comment_end_responses.value
            self.set_regular_response(response)

            return self.response_data
        except:
            return self.get_error_response_data()
