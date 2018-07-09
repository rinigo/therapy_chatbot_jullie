import logging
import numpy as np
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class OYSMeaninglessInARowResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            responses = self.__create_oys_after_meaningless_in_a_row()

            self.response_data['regular'] = responses

            return self.response_data
        except:
            logging.exception('')
            return self.response_data

    def __create_oys_after_meaningless_in_a_row(self):
        qr = [
            ["okay!"],
            ["i see:)"],
            ["gotcha!"],
            ["right!"],
            ["alright!"],
        ]
        oys = [
            ["just let you know im always here"],
            ["you know i am always here for you ok?"],
            ["I love to be here for you"],
            ["it is always glad to talk to you"],
            ["it is always good feeling to listen to you"]
        ]
        encourage = [
            ["and you can tell me anything whenever you ready😋"],
            ["you know, you can come talk to me anytime you want, no rush😜"],
            ["take your time and please come back here whenever you ready🤗"],
            ["again, you just come talk to me whenever you want, never feel forced🤓"],
            ["i think you need little break now..just come back whenever you would like to😋"]
        ]
        np.random.shuffle(qr)
        np.random.shuffle(oys)
        np.random.shuffle(encourage)
        return qr[0] + oys[0] + encourage[0]