import logging
import numpy as np
import models
from common.constant.df_from_csv import WORD_LIST_FOR_CMP
from common.word_format.word_formatter import WordFormatter
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
from core.nlp.df_generator.sentiment_score_df_generator import SentimentScoreDFGenerator
from core.nlp.df_generator.text_kw_df_generator import TextKwDFGenerator
from core.nlp.normalizer.message_normalizer import MessageNormalizer


class PreviousSentCMPResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            previous_msg = models.Message.fetch_previous_msg(self.user.id)
            w_toks = WordFormatter.SToks2WToks([previous_msg])

            message_normalizer = MessageNormalizer()
            df = message_normalizer(w_toks, self.user.sender_id, from_preprocessor=False)
            text_kw_df_gengerator = TextKwDFGenerator()
            text_kw_df = text_kw_df_gengerator(df)


            sentiment_score_df_generator = SentimentScoreDFGenerator()
            sentiment_score_df = sentiment_score_df_generator(df, text_kw_df)

            responses = self.create_cmp(df, sentiment_score_df, self.response_data)
            self.response_data['regular'] = responses

            return self.response_data
        except:
            logging.exception('')
            return self.response_data

    @classmethod
    def create_cmp(cls, text_df, sentiment_score_df, response_data):
        try:
            cmp_sent_list = []
            target_word_row = text_df[text_df["base_form"].isin(WORD_LIST_FOR_CMP.word.tolist())].iloc[-1]
            alternative_sentiment_words = \
                WORD_LIST_FOR_CMP.loc[WORD_LIST_FOR_CMP.word.isin([target_word_row.base_form]), "cmp_word"].values[0]
            alternative_sentiment_word = np.random.choice(alternative_sentiment_words.split(), 1)[0]

            subject_list = ["you ", "it ", "that ", ""]
            auxiliary_verb_list = ["must ", "should "]
            verb_list_for_auxiliary_verb = ["feel ", "be "]
            sounds_seems_list = ["sound", "sound like"]
            adverb_list = ["really ", "seriously ", "pretty ", "very "]
            subject = np.random.choice(subject_list, 1)[0]

            if subject in ["it ", "that ", ""]:
                sounds_seems_list = ["sounds", "sounds like"]

            adverb = np.random.choice(adverb_list, 1)[0] if any(
                [i <= -120 for i in sentiment_score_df.nscore.values]) else ""
            word_type_before_sentiment_word = np.random.choice(["auxiliary_verb", "sound_seem"], 1)[0]
            if word_type_before_sentiment_word == "auxiliary_verb":
                auxiliary_verb = np.random.choice(auxiliary_verb_list, 1)[0]
                verb_for_auxiliary_verb = np.random.choice(verb_list_for_auxiliary_verb, 1)[0]
                verb = auxiliary_verb + verb_for_auxiliary_verb
                main_words = subject + verb + adverb + alternative_sentiment_word + ".."
            else:
                verb = np.random.choice(sounds_seems_list, 1)[0] + " "
                main_words = subject + verb + adverb + alternative_sentiment_word + ".."

            cmp_sent_list.append(main_words)

            print("\nCMP_SENT_LIST\n{}".format(cmp_sent_list))

            return cmp_sent_list
        except:
            logging.exception('')
            return []
