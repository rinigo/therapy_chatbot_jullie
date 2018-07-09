import logging
import pandas as pd
from common.constant.df_from_csv import SUICIDE_WORD_DF


class SuicideDetector:
    @classmethod
    def is_suicidal(cls, text_df):
        try:
            if text_df is None:
                return False

            for sidx in set(text_df.sidx.values):
                if cls.__has_suicidal_word(text_df, sidx):
                    return True
            else:
                return False
        except:
            logging.exception('')
            return False

    @classmethod
    def __has_suicidal_word(cls, text_df, sidx):
        target_text_df = text_df[text_df.sidx == sidx]

        sc_words_in_msg = [[row.widx, row.word] for idx, row in target_text_df.iterrows()
                           if row.word in SUICIDE_WORD_DF['word1'].values]
        sc_words_in_msg = pd.DataFrame(sc_words_in_msg)

        if sc_words_in_msg.empty:
            return False

        sc_words_in_msg.columns = ['widx', 'word1']

        sc_subjs = cls.__find_sc_owner(sc_words_in_msg, target_text_df)
        sc_1st_person_subj = sc_subjs[sc_subjs.owner.isin(['i', 'me'])]

        if sc_1st_person_subj.empty:
            return False

        sc_without_negation = cls.__find_sc_without_negation(sc_1st_person_subj, target_text_df)
        sc_without_negation = sc_without_negation[sc_without_negation.negation == 'False']

        if sc_without_negation.empty:
            return False

        for idx, row in sc_without_negation.iterrows():
            should_check_second = type(SUICIDE_WORD_DF[SUICIDE_WORD_DF.word1 == row.word1].word2.tolist()[0]) == str

            if should_check_second:
                target_range = target_text_df[(target_text_df.widx > row.widx) & (target_text_df.widx <= row.widx + 3)]

                is_suicide_word_in_range = any(
                    i in SUICIDE_WORD_DF[SUICIDE_WORD_DF.word1 == row.word1].word2.tolist()
                    for i in target_range.word.tolist()
                )

                if is_suicide_word_in_range:
                    return True
            else:
                return True

        return False

    @staticmethod
    def __find_sc_owner(suicidal_df, target_text_df):
        suicidal_df['owner'] = 'Unknown'

        for idx, row in suicidal_df.iterrows():

            target_widx_range = target_text_df[target_text_df.widx < row.widx]

            for ridx, target_row in target_widx_range.iloc[::-1].iterrows():

                if target_row.pos == 'PRP':
                    suicidal_df.loc[idx, 'owner'] = target_row.word
                elif target_row.pos in {'CC', 'NNP', 'IN', 'WP'}:
                    suicidal_df.loc[idx, 'owner'] = 'Not found'
                else:
                    continue
                break

        return suicidal_df

    @staticmethod
    def __find_sc_without_negation(suicidal_df, target_text_df):
        suicidal_df['negation'] = "Unknown"

        for idx, row in suicidal_df.iterrows():

            target_widx_range = target_text_df[target_text_df.widx < row.widx]

            if row.word1 in {'live', 'living'}:
                suicidal_df.loc[idx, 'negation'] = 'False'
                continue

            for ridx, target_row in target_widx_range.iloc[::-1].iterrows():

                if target_row.word in {'not', 'never'}:
                    suicidal_df.loc[idx, 'negation'] = 'True'
                elif target_row.pos in {'CC', 'NNP', 'IN'}:
                    suicidal_df.loc[idx, 'negation'] = 'False'
                else:
                    continue
                break
            else:
                suicidal_df.loc[idx, 'negation'] = 'False'

        return suicidal_df
