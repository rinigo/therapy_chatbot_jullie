import logging
import numpy as np
from common.constant.df_from_csv import LDF, BAD_WORDS_DF
from common.word_format.df_utils import Nlp_util
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class CQLResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            responses = self.create_cql_response()
            self.response_data['regular'] = responses

            return self.response_data
        except:
            logging.exception('')
            return self.response_data

    def create_cql_response(self):
        labeling = self.generate_labeling()

        if not labeling:
            return []

        while not labeling[0][-1].isalpha():
            labeling[0] = labeling[0][:-1]

        cql = [labeling[0] + ' right?']

        return cql

    def generate_labeling(self):
        try:
            repeat_sentiment = self.get_sentiment_of_repeat_target_sent(self.message.text_df,
                                                                        self.message.sentiment_score_df)
            print("\nRepeat Sentiment\n{}".format(repeat_sentiment))

            if repeat_sentiment == "negative":
                return self.select_labeling_option('ng')
            elif repeat_sentiment == "neutral":
                return self.select_labeling_option('nt')
            elif repeat_sentiment == "positive":
                return self.select_labeling_option('p')
            else:
                return []

        except:
            logging.exception('')
            return []

    @staticmethod
    def select_labeling_option(e_type):
        labeling_sent = np.random.choice(LDF[LDF.id == e_type].labeling.values, 1)[0]

        if e_type == "ng":
            labeling_sent += np.random.choice(["😥", "😣", "😔", "😞"], 1)[0]
        elif e_type == "nt":
            labeling_sent += np.random.choice(["😐", "🤔", "😲", "😯"], 1)[0]
        elif e_type == "p":
            labeling_sent += np.random.choice(["☺️", "😚", "😉", "😁"], 1)[0]

        return [labeling_sent]

    @classmethod
    def get_sentiment_of_repeat_target_sent(cls, text_df, sentiment_score_df):
        try:
            if text_df is None:
                return None

            repeat_df = text_df

            delete_sidx_list = list(
                sentiment_score_df[sentiment_score_df.nscore.isin([0]) & sentiment_score_df.pscore.isin([0])].sidx)
            delete_sidx_list.extend(list(text_df[text_df.word.isin(["you", "jullie", "j"])].sidx))
            delete_sidx_list.extend(cls.__get_sidx_with_bad_words(repeat_df))
            delete_sidx_list.extend(cls.__get_sidx_of_not_basic_svo_sent(repeat_df))

            if len(set(delete_sidx_list)) == len(set(repeat_df.sidx.values)):
                return None
            target_sentiment_score_df = sentiment_score_df[~sentiment_score_df.sidx.isin(list(set(delete_sidx_list)))]
            print("\nTarget Sentiment Score Df\n{}".format(target_sentiment_score_df))

            if any(abs(target_sentiment_score_df.nscore) > 0) and any(target_sentiment_score_df.pscore > 0):
                return "neutral"
            elif any(abs(target_sentiment_score_df.nscore) > 0) and all(target_sentiment_score_df.pscore == 0):
                return "negative"
            elif all(abs(target_sentiment_score_df.nscore) == 0) and any(target_sentiment_score_df.pscore > 0):
                return "positive"
            else:
                return None

        except:
            logging.exception('')
            return None

    @staticmethod
    def __get_sidx_with_bad_words(text_df):
        return text_df[text_df.word.isin(BAD_WORDS_DF.word)].sidx.values

    @staticmethod
    def __get_sidx_of_not_basic_svo_sent(text_df):
        delete_sidx_list = []
        for sidx in set(text_df.sidx.values):
            df = text_df[text_df.sidx == sidx]
            noun_list = Nlp_util.make_noun_list(df)
            verb_list = Nlp_util.make_verb_list(df, type="normal")

            # catch the case such as "Dont judge me"
            if Nlp_util.is_any_verb_before_first_noun(noun_list, verb_list):
                delete_sidx_list.append(sidx)
            # catch the case such as "the situation horrible as like he said"
            elif not Nlp_util.is_any_verb_for_first_noun(noun_list, verb_list):
                delete_sidx_list.append(sidx)
            else:
                pass

        return delete_sidx_list
