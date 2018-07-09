import logging
from core.nlp.response_generator.product.cct.cmp_response_generator import CMPResponseGenerator
from core.nlp.response_generator.product.cct.repeat_response_generator import RepeatResponseGenerator
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class BothCmpANdRepeatResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            args = self.user, self.message, self.message_type
            repeat_generator = RepeatResponseGenerator(*args)
            repeat_response = repeat_generator()
            repeat = repeat_response['regular']

            cmp_generator = CMPResponseGenerator(*args)
            cmp_response = cmp_generator()
            cmp = cmp_response['regular']

            self.response_data['regular'] = repeat + cmp

            return self.response_data
        except:
            logging.exception('')
            return self.response_data