import logging
import numpy as np

from common.constant.string_constant import StringConstant
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class NeedHelpResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            responses = self.__select_responses_for_need_help()

            self.response_data['regular'] = responses

            return self.response_data
        except:
            return self.get_error_response_data()

    @classmethod
    def __select_responses_for_need_help(cls):
        try:
            options = StringConstant.responses_for_need_help.value
            np.random.shuffle(options)

            return options[0]
        except:
            logging.exception('')
            return []
