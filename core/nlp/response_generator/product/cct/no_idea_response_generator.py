import numpy as np
from common.constant.string_constant import StringConstant
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class NoIdeaResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            responses = np.random.choice(StringConstant.guess_advise_list.value, 1)[0]

            self.response_data['regular'] = responses

            return self.response_data
        except:
            return self.get_error_response_data()
