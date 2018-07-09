from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
import logging
from common.constant.emojis import quick_response_emoji_list, QuickResponseEmoji
from common.constant.df_from_csv import QRDF, NGDF
from common.word_format.df_utils import Df_util
import numpy as np


class QuickResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            if self.message.sentiment_score_df is None:
                return self.__get_response_candidates('nt')

            is_negative = any([i != 0 for i in self.message.sentiment_score_df.nscore.values])
            is_positive = any([i >= 100 for i in self.message.sentiment_score_df.pscore.values]) \
                          and Df_util.anything_isin(NGDF, self.message.text_df.word)
            is_really_negative = any([i <= -150 for i in self.message.sentiment_score_df.nscore.values])

            if is_really_negative:
                responses = self.__get_response_candidates('rng')
            elif is_negative and not is_positive:
                responses = self.__get_response_candidates('ng')
            elif is_positive and not is_negative:
                responses = self.__get_response_candidates('p')
            else:
                responses = self.__get_response_candidates('nt')

            self.response_data['regular'] = responses

            return self.response_data
        except:
            logging.exception('')
            return self.response_data

    def __get_response_candidates(self, e_type):
        try:
            quick_response = np.random.choice(QRDF[QRDF.id == 'ng'].qresp.tolist(), 1)[0]
            quick_response = np.random.choice([quick_response, quick_response.lower()], 1)[0]

            rng_options = ["omg", "really", "i am so sorry for you", "sorry to hear that"]
            if e_type == "rng":
                quick_response = np.random.choice(rng_options, 1)[0]
            elif quick_response in quick_response_emoji_list:
                quick_response = QuickResponseEmoji[quick_response].value
            else:
                if e_type == "ng":
                    quick_response += np.random.choice(["", "😣", "😔", "😞"], 1)[0]
                elif e_type == "nt":
                    quick_response += np.random.choice(["", "😐", "🤔", "😯"], 1)[0]
                elif e_type == "p":
                    quick_response += np.random.choice(["", "☺️", "😉", "😁"], 1)[0]

            return [quick_response]
        except:
            logging.exception('')
            return []
