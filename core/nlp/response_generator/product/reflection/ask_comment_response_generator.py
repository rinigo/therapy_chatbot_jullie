from common.constant.session_status import SessionStatus
from common.constant.string_constant import StringConstant
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class AskCommentResponseGenerator(BaseResponseGenerator):
    def __call__(self, therapy_session):
        try:
            therapy_session.change_status(SessionStatus.asking_comment.value)

            self.response_data = self.__create_response_for_asking_comment()

            return self.response_data
        except:
            return self.get_error_response_data()

    def __create_response_for_asking_comment(self):
        try:
            responses = StringConstant.ask_comment_end_responses.value
            self.set_regular_response(responses)

            return self.response_data
        except:
            return self.get_error_response_data()
