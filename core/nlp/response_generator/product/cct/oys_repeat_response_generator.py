from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
import logging
import numpy as np


class OYSRepeatResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            responses = self.__create_oys_after_repeat()
            self.response_data['regular'] = responses

            return self.response_data
        except:
            logging.exception('')
            return self.response_data

    def __create_oys_after_repeat(self):
        options = [
            ["so thats the thing stuck in your head now😣"],
            ["so it is the thing kinda bothering you now🤔"],
            ["so that is what comes to your mind now😥"],
            ["so that is what you are concerned about🧐"],
            ["so that's what your mind dwells on now😢"],
            ["so thats the thing stressing you now😞"],
        ]
        np.random.shuffle(options)
        return options[0]
