import logging
import numpy as np
from common.constant.df_from_csv import WORD_LIST_FOR_CMP
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator


class CMPResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        return self.create_cmp()

    def create_cmp(self):
        try:
            cmp_sent_list = []

            target_word_row = \
                self.message.text_df[self.message.text_df["base_form"].isin(WORD_LIST_FOR_CMP.word.tolist())].iloc[-1]

            alternative_sentiment_words = \
                WORD_LIST_FOR_CMP.loc[WORD_LIST_FOR_CMP.word.isin([target_word_row.base_form]), "cmp_word"].values[
                    0]
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
                [i <= -120 for i in self.message.sentiment_score_df.nscore.values]) else ""
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

            self.response_data['regular'] = cmp_sent_list

            return self.response_data
        except:
            logging.exception('')
            return self.response_data
