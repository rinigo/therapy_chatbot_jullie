import logging
import pandas as pd
from nltk import StanfordPOSTagger
from common.word_format.df_utils import Nlp_util, Df_util

class PosTagger:
    @classmethod
    def add_pos_tag(cls, df):
        df = cls.__add_basic_pos_tag(df)
        dic_for_correction = {"feel": "VB", "talk": "VB", 'u': 'PRP', 'i': 'PRP', 'know': 'VB', 'move': 'VB',
                              'ask': 'VB', 'dont': 'RB', 'don`t': 'RB', 'didnt': 'RB', 'did\'t': 'RB', "am": 'VB',
                              "get": 'VB', "ex": "NN", "hate": "VB", "wish": "VB", "not": "NO", "never": "NO"}

        df = cls.__correct_pos_tag(df, dic_for_correction)

        df = cls.__convert_pos_of_love(df)

        return df

    @staticmethod
    def __add_basic_pos_tag(df):
        pos_path_jar = "./stanford-postagger-full-2017-06-09/stanford-postagger.jar"
        pos_path_model = "./stanford-postagger-full-2017-06-09/models/english-left3words-distsim.tagger"
        pos_tagger = StanfordPOSTagger(pos_path_model, pos_path_jar)

        pos = [pos_tagger.tag(s) for s in [df.word]]

        pos = [i[1] for i in pos[0]]

        pos = pd.DataFrame(pos)

        df['pos'] = pos

        return df

    @staticmethod
    def __correct_pos_tag(df, dic):
        if any(df["word"].isin(dic.keys())):
            df.loc[df["word"].isin(dic.keys()), "pos"] = df[df["word"].isin(dic.keys())].apply(
                lambda row: dic[row["word"]], axis=1)

        if any(df["word"].isin(["that", "it", "this"])):
            idx_list_of_kws = Nlp_util.get_idx_list_of_word_list(["that", "it", "this"], df["word"])
            for idx_of_kw in idx_list_of_kws:
                if idx_of_kw == len(df)-1 or df.loc[idx_of_kw+1, "pos"] not in Nlp_util.pos_PRPs + Nlp_util.pos_NOUNs:
                    df.loc[idx_of_kw, "pos"] = "NN"
                else:
                    pass

        if Df_util.anything_isin(["like", "care", "guess", "need"], df["word"]):
            idx_list_of_like = Nlp_util.get_idx_list_of_word_list(["like", "care","guess", "need"], df["word"])
            for idx_of_like in idx_list_of_like:
                if not idx_of_like == 0 and df.loc[idx_of_like-1, "pos"] in Nlp_util.pos_NOUNs+Nlp_util.pos_PRPs:
                    df.loc[idx_of_like, "pos"] = "VB"
                else:
                    pass
        if Df_util.anything_isin(["work"], df["word"]):
            idx_list_of_work = Nlp_util.get_idx_list_of_word_list(["work"], df["word"])
            for idx_of_work in idx_list_of_work:
                if not idx_of_work == 0 and df.loc[idx_of_work-1, "word"] in ["this"]:
                    df.loc[idx_of_work, "pos"] = "VB"
                else:
                    pass

        return df

    @staticmethod
    def __convert_pos_of_love(df):
        try:
            if any(df.word == 'love'):
                love_rows = df[df.word == 'love']
                for row_idx, row in love_rows.iterrows():
                    search_range = df[(df.sidx == row.sidx) & (df.widx < row.widx)].word
                    if any(i == 'i' for i in search_range):
                        df.at[row_idx, 'pos'] = 'VBP'

            return df
        except:
            logging.exception('')
            return df
