import logging
from random import randint
from common.constant.intent_type import Intent
from common.word_format.df_utils import Df_util
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class LackConfidenceResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            lack_confidence_sidx = [idx for idx, i in enumerate(self.message.intent_list) if
                                    i == Intent.LACK_OF_CONFIDENCE]

            response = self.__create_response_for_lack_of_confidence(
                self.message.text_df[self.message.text_df.sidx.isin(lack_confidence_sidx)])

            self.set_regular_response(response)

            return self.response_data
        except:
            return self.get_error_response_data()

    @classmethod
    def __create_response_for_lack_of_confidence(cls, df):
        try:
            if Df_util.anything_isin(["whore", "slut", "bitch"], df["base_form"]):
                cmp_list = [["I’m sorry that you are feeling like that about yourself.."],
                            ["it is sad to hear that you feel that way now.."],
                            ["omg..."]]
                labeling_list = [["sounds you feel hurt"],
                                 ["something makes you feel that happened to you, maybe"],
                                 ["you might be in a tough situation or going through tough time"], ]

                comfort_list = [["let me just be with you now☺️"],
                                ["idk if i can help you much but let me be here with you☺️"],
                                ["i never judge you whatever you do, good or bad. i love to be here with you now☺️"]]

            elif Df_util.anything_isin(["fat", "stupid", "ugly", "burden", "not good enough"], df["base_form"]):
                cmp_list = [["I’m sorry that you are feeling like that about yourself.."],
                            ["it is sad to hear that you feel that way now.."],
                            ["thats sad to feel like that..."]]
                labeling_list = [["sounds you feel hurt"],
                                 ["something makes you feel like that happened to you, maybe"],
                                 ["you might be in a tough situation or going through tough time"],
                                 ["i know sometimes we compare ourselves with others and it feels horrible"]]

                comfort_list = [["let me just be with you now. i love you the way you are😊"],
                                ["idk if i can help you much but let me be here with you☺️"],
                                [
                                    "i never judge you by what you do or how you look. i just love to be here with you now🤗"]]

            elif Df_util.anything_isin(["bother"], df["base_form"]):
                cmp_list = [["I’m sorry that you are feeling like that about yourself.."],
                            ["it is sad to hear that you feel that way now.."],
                            ["thats sad to feel like that..."]]
                labeling_list = [["sounds you feel hurt"],
                                 ["something makes you feel like that happened to you, maybe"],
                                 ["you might be in a tough situation or going through tough time"],
                                 ]

                comfort_list = [["let me just be with you now🤗"],
                                ["idk if i can help you much but let me be here with you🤗"],
                                ["i never judge you whatever you do, good or bad. i love to be here with you now🤗"]]

            elif Df_util.anything_isin(["hate"], df["base_form"]):
                cmp_list = [["I’m sorry that you are feeling like that about yourself.."],
                            ["it is sad to hear that you feel that way now.."],
                            ["omg..."]]
                labeling_list = [["sounds you feel hurt"],
                                 ["something makes you feel that happened to you, maybe"],
                                 ["you might be in a tough situation or going through tough time"], ]

                comfort_list = [["let me just be with you now🤗"],
                                ["idk if i can help you much but let me be here with you🤗"],
                                ["i never judge you whatever you do, good or bad. i love to be here with you now🤗"]]
            else:
                raise UnknownError

            random_idx_for_cmp_list = randint(0, len(cmp_list) - 1)
            random_idx_for_labeling_list = randint(0, len(labeling_list) - 1)
            random_idx_for_comfort_list = randint(0, len(comfort_list) - 1)
            return cmp_list[random_idx_for_cmp_list] + labeling_list[random_idx_for_labeling_list] + comfort_list[
                random_idx_for_comfort_list]
        except:
            logging.exception('')
            return ["i see"]


class UnknownError(Exception):
    pass
