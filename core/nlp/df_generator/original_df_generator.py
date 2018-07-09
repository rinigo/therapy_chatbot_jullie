import logging
import pandas as pd
from core.nlp.pos_tagger import PosTagger
from textblob import Word
from common.word_format.df_utils import Nlp_util


class OriginalDFGenerator:
    @classmethod
    def create_original_df_by_w_toks(cls, w_toks):
        try:
            list_for_text_df = [[sidx, widx, w] for sidx, s in enumerate(w_toks) for widx, w in enumerate(s)]

            original_df = pd.DataFrame(list_for_text_df)

            if original_df.empty:
                return None
            else:
                original_df.columns = ['sidx', 'widx', 'word']

            original_df = PosTagger.add_pos_tag(original_df)

            original_df.columns = ['sidx', 'widx', 'word', 'pos']

            original_df["base_form"] = original_df.apply(lambda row: cls.create_base_form(row["word"], row["pos"]), axis=1)

            return original_df
        except:
            logging.exception('')

    @staticmethod
    def create_base_form(word, word_pos):
        if word_pos in Nlp_util.pos_NOUNs:
            return Word(word).lemmatize("n")
        elif word_pos in Nlp_util.pos_VERBs:
            if word in ["texting"]:
                return "text"
            else:
                return Word(word).lemmatize("v")
        elif word_pos in Nlp_util.pos_ADVERBs:
            return Word(word).lemmatize("r")
        elif word_pos in Nlp_util.pos_ADJECTIVEs:
            return Word(word).lemmatize("a")
        else:
            return Word(word).lemmatize("n")
