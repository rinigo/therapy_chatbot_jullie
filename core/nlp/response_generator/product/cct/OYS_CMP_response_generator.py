from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
import logging
import numpy as np


class OYSCMPResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            responses = self.__create_oys_after_cmp()

            self.response_data['regular'] = responses

            return self.response_data
        except:
            logging.exception('')
            return self.response_data

    def __create_oys_after_cmp(self):
        options = [
            ["Life is tough😞", "I am here for you now"],
            ["I am sorry for you..😢", "Just vent me anything you want"],
            ["Life is not always easy right☹️", "Let me just be with you"]
        ]
        np.random.shuffle(options)
        return options[0]
