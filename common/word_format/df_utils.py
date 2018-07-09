import string
from textblob import Word
import nltk
from common.word_format.word_formatter import WordFormatter
import logging

class UnknownError:
    pass


class Df_util(object):

    @staticmethod
    def anything_isin(word_list, series):
        for word in word_list:
            tokenized_word = nltk.word_tokenize(word)
            if len(tokenized_word) == 1:
                if any(series.isin(word_list)):
                    return True
                else:
                    pass

            else:
                ngram_list_of_the_series = Nlp_util.create_ngrams(WordFormatter.Series2Str(series),
                                                                  len(tokenized_word))
                if tokenized_word in ngram_list_of_the_series:
                    return True
                else:
                    pass
        return False

    # word1のidxとword2のidxで続きになってるものを発見し、続きになっているword1のidxをリストで返す
    @staticmethod
    def make_pair_words_idx_list(word1_idx_list, word2_idx_list):
        return list(set(word1_idx_list) & set(list(map(lambda x: x - 1, word2_idx_list))))

    @staticmethod
    def nothing_isin(word_list, series):
        return all(series.isin(word_list) == False)


class Nlp_util(object):
    pos_NOUNs = ["NN", "NNS", "NNP", "NNPS"]
    pos_PRPs = ["PRP"]
    pos_VERBs = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
    pos_ADVERBs = ["RB", "RBR", "RBS"]
    pos_ADJECTIVEs = ["JJ", "JJR", "JJS"]
    DO_TYPE = ["Do", "Did", "Didnt", "Does", "Doesnt", "Dont", "do", "dont", "did", "didnt", "does", "doesnt"]
    BE_TYPE = ["are", "arent", "were", "werent", "is","isnt", "was", "wasnt", "am"]
    NO_TYPE = ["not", "no", "never"]
    SHOULD_TYPE = ["Should", "should", "better", "have to", "has to", "had to"]
    CAN_TYPE = ["Can", "Could", "Cant", "Couldnt", "can", "could", "cant", "couldnt"]
    THINK_TYPE = ["think", "feel", "consider", "thought", "felt", "considered"]
    IDEA_TYPE = ["idea", "opinion", "suggestion", "clue", "solution", "advice"]
    # what would be goodなど主語の無いタイプにつく可能性がある単語
    SP_TYPE1 = ["good", "better", "best", "next", "step"]
    SP_TYPE2 = ["like", "love"]
    INDICATE_OTHERS = ["everyone", "everybody", "guy","girl", "anyone", "boy", "man", "buddy","friend"]

    @staticmethod
    def adjust_be_verb_for_changed_subject(word, word_pos, word_idx, noun_list):
        if word in {"am", "are", "was", "were"}:

            if any(noun_list.index < word_idx) and noun_list.loc[:word_idx].iloc[-1]["word"] == "you":
                return "were" if word_pos in {"VBD", "VBN"} else "are"
            elif any(noun_list.index < word_idx) and noun_list.loc[:word_idx].iloc[-1]["word"] == "i":
                return "was" if word_pos in {"VBD", "VBN"} else "am"
            else:
                return word
        else:
            return word

    @staticmethod
    def change_object_pronoun_to_pronoun(word):
        dic_to_change = {
            "us": "you guys ",
            "me": "you",
            "him": "he",
            "her": "she",
            "them": "they",
            "myself": "yourself",
            "yourself": "myself",
        }

        if word in dic_to_change.keys():
            return dic_to_change[word]
        else:
            return word


    @staticmethod
    def change_subject_other_way_around(word, word_idx=None, word_series=None, exception_list={}):
        dic_to_change = {
            "you": "i",
            "i": "you",
            "we": "you guys",
            "this": "that",
            "these": "those",
            "our": "your",
            "my": "your",
            "me": "you",
            "your": "my",
            "yours": "mine",
            "myself": "yourself",
            "yourself": "myself",
        }

        list_to_change_to_me = {
            "tell",
            "ask",
            "like",
            "love",
            "to",
            "for",
            "from",
            "with",
            "about",
            "call",
            "about",
            "upon",
            "on",
            "with",
            "by",
            "at",
        }
        if word in dic_to_change.keys() and word not in exception_list:
            if word_idx is None or word != "you" or word_idx == 0:
                return dic_to_change[word]
            else:
                if Word(word_series.loc[word_idx-1]).lemmatize("v") in list_to_change_to_me:
                    return "me"
                else:
                    return "i"
        return word

    @staticmethod
    def cut_end_symbol_df(df):
        try:
            while all(not word.isalpha() for word in df.iloc[-1]["word"]):
                df = df[:-1]
                if len(df) == 0:
                    return df
            return df
        except:
            logging.exception('')
            return df


    @staticmethod
    def cut_unnecessary_words(df):
        try:
            # df = df.drop(len(df) - 1) if Nlp_util.is_last_word({"?","."}, df) else df
            df = Nlp_util.cut_end_symbol_df(df)
            if len(df) == 0:
                return df
            elif len(Nlp_util.make_noun_list(df)) < 2:
                return df
            elif df.iloc[-2:]["word"].iloc[0] in Nlp_util.DO_TYPE + Nlp_util.BE_TYPE and df.iloc[-2:]["pos"].iloc[
                1] == "PRP":
                return df.iloc[:-2] if not df.iloc[-3]["word"] == "," else df.iloc[:-3]
            else:
                return df
        except:
            logging.exception('')
            return df

    @staticmethod
    def change_subject_dt_to_nn(df):
        verb_list = df[df["pos"].isin(Nlp_util.pos_VERBs)]
        dt_idx_list = list(df[df["pos"].isin(["DT"])].loc[df["word"] != "the"].index)
        # dt_idx_list = df.where(df["pos"].isin(["DT"]) and df["word"] != "the")
        if len(verb_list) < 2:
            df.loc[dt_idx_list, "pos"] = "NN"
            return df
        # remove dt with subject before subject in between verbs
        verb_idx_list = iter(verb_list.index)
        for verb_idx1, verb_idx2 in zip(verb_idx_list, verb_idx_list):
            if Df_util.anything_isin(Nlp_util.pos_NOUNs + Nlp_util.pos_PRPs, df.loc[verb_idx1:verb_idx2, "pos"]):
                for dt_idx in dt_idx_list:
                    if verb_idx1 < dt_idx < verb_idx2:
                        dt_idx_list.remove(dt_idx)
                    else:
                        pass
            else:
                pass

        if len(dt_idx_list) > 0:
            df.loc[dt_idx_list, "pos"] = "NN"
            return df
        else:
            return df

    @staticmethod
    def convert_series_to_list(series):
        return "".join(
            [" " + i if not i.startswith("'") and i not in string.punctuation else i for i in series]).strip()

    @staticmethod
    def change_pos_of_word(df, word_dic):
        df.loc[df["word"].isin(word_dic.keys()), "pos"] = df[df["word"].isin(word_dic.keys())].apply(
            lambda row: word_dic[row["word"]], axis=1)
        return df

    @staticmethod
    def create_ngrams(text, split_num):
        text = text.split(' ')
        ngram_list = []
        for i in range(len(text) - split_num + 1):
            ngram_list.append(text[i:i + split_num])
        return ngram_list

    @staticmethod
    def convert_objective_noun_to_nominative(noun):
        objective_nominative_dict = {"him": "he", "her": "she", "them": "they"}
        if noun in objective_nominative_dict.keys():
            noun_nominative = objective_nominative_dict[noun]
        else:
            noun_nominative = noun

        return noun_nominative

    @staticmethod
    def convert_nominative_noun_to_objective(noun):
        nominative_objective_dict = {"he":"him", "she":"her", "they":"them"}
        if noun in nominative_objective_dict.keys():
            noun_objective = nominative_objective_dict[noun]
        else:
            noun_objective = noun

        return noun_objective


    @staticmethod
    def change_verb_form(subject, verb, verb_pos):
        verb_original_form = Word(verb).lemmatize("v")
        # be動詞かどうか
        if verb in {"be", "am", "are", "is", "was", "were"}:
            if verb_pos in {"VBD", "VBN"}:
                if subject in {"you", "they", "we"}:
                    verb_suited_form_to_subject = "were"
                else:
                    verb_suited_form_to_subject = "was"
            else:
                if subject in {"i"}:
                    verb_suited_form_to_subject = "am"
                elif subject in {"you", "they", "we"}:
                    verb_suited_form_to_subject = "are"
                else:
                    verb_suited_form_to_subject = "is"

        else:
            if verb_pos in {"VBD", "VBN"}:
                # 普通の動詞で過去形だった場合そのまま返す！
                verb_suited_form_to_subject = verb
            else:
                if subject in {"i", "you", "they", "we", "you guys"}:
                    # 主語が上記で動詞がbe動詞でも無く過去形でもない場合はその動詞の原型がv2
                    verb_suited_form_to_subject = verb
                else:
                    # 主語がsheとかの場合、一旦原型に戻したものを複数形にして返す
                    if verb in {"have"}:
                        verb_suited_form_to_subject = "has"
                    else:
                        verb_suited_form_to_subject = Word(verb_original_form).pluralize()

        verb_list = [verb_original_form, verb_suited_form_to_subject]
        return verb_list

    @staticmethod
    def get_idx_list_of_word(word, series):
        return list(series[series == word].index) if Df_util.anything_isin([word], series) else []
    @staticmethod
    def get_idx_list_of_word_list(word_list, series):
        return list(series[series.isin(word_list)].index) if Df_util.anything_isin(word_list, series) else []

    @staticmethod
    def get_idx_list_of_idiom(idiom, series):
        tokenized_word = nltk.word_tokenize(idiom)
        ngram_list_of_the_series = Nlp_util.create_ngrams(WordFormatter.Series2Str(series),
                                                          len(tokenized_word))
        return [idx for idx, ngram in enumerate(ngram_list_of_the_series) if ngram == tokenized_word]

    @staticmethod
    def get_idx_list_of_idiom_list(idiom_list, series):
        idx_list_of_idiom = []
        for idiom in idiom_list:
            idx_list_of_idiom += Nlp_util.get_idx_list_of_idiom(idiom, series)
        return idx_list_of_idiom

    @staticmethod
    def get_first_verb(noun_list, verb_list):
        if len(noun_list) == 0 or len(verb_list) == 0:
            return False
        if any(verb_list.index > noun_list.index[0]):
            return verb_list[verb_list.index > noun_list.index[0]].iloc[0]
        else:
            return None

    @staticmethod
    def get_second_verb(noun_list, verb_list):
        if len(noun_list) == 0 or len(verb_list) == 0:
            return ""
        return verb_list[Nlp_util.get_second_subject(noun_list, verb_list).name:].iloc[0]

    @staticmethod
    def get_second_subject(noun_list, verb_list):
        if len(noun_list) == 0 or len(verb_list) == 0:
            return ""
        first_verb_idx = Nlp_util.get_first_verb(noun_list, verb_list).name
        second_verb_idx = 1
        for index, row in verb_list.loc[first_verb_idx:].iterrows():
            if any(verb_list.loc[first_verb_idx:index].isin(noun_list.index)):
                second_verb_idx = index
                break
            else:
                pass
        return noun_list[:second_verb_idx].iloc[-1]

    @staticmethod
    def get_wordsDF_of_wordlist_after_idx(df, word_list, idx, column_name):
        return df.loc[idx:,:][df.loc[idx:, column_name].isin(word_list)]


    @staticmethod
    def has_double_subjects(noun_list, verb_list):
        if len(noun_list) < 2 or len(verb_list) == 0:
            return False
        return any(verb_list.index > noun_list.index[1])

    @staticmethod
    def hasnt_any_verb_and_subject(noun_list, verb_list):
        return len(noun_list) < 1 and len(verb_list) < 1

    # find S + V pair
    @staticmethod
    def exists_any_noun_verb_pair(noun_list, verb_list):
        if len(noun_list) == 0 or len(verb_list) == 0:
            return False
        # when all verbs locates before first noun
        elif all(verb_list.index < noun_list.index[0]):
            return False
        else:
            return True

    @staticmethod
    def are_words1_words2_words3_in_order(df, words1_list, words2_list, words3_list=[], df_column="base_form", exception_list=[]):
    #     ex) words1_list = ["he", "boyfriend"], words2_list = ["not pay", "never pay"], words3_list = ["attention", "bill"]

        words2_idx_list = Nlp_util.get_idx_list_of_idiom_list(words2_list, df[df_column])
        if len(words2_idx_list) == 0:
            return False
        elif len(exception_list) !=0 and Df_util.anything_isin(exception_list, df[df_column]):
            return False
        else:
            for words2_idx in words2_idx_list:
                if Df_util.anything_isin(words1_list, df.loc[:words2_idx , df_column]):
                    if len(words3_list) == 0 or Df_util.anything_isin(words3_list, df.loc[words2_idx: , df_column]):
                        return True
                    else:
                        pass
                else:
                    pass
            return False



    @staticmethod
    def is_first_word_in(word_list, df):
        return df.iloc[0].word in word_list

    @staticmethod
    def is_first_verb_in(word_list, noun_list, verb_list, column_name="word"):
        if len(noun_list) == 0 or len(verb_list) == 0:
            return False
        elif any(verb_list.index > noun_list.index[0]):
            return verb_list[column_name][verb_list.index > noun_list.index[0]].iloc[0] in word_list
        else:
            return False

    @staticmethod
    def is_first_adj_after_first_sub_in(word_list, noun_list, adj_list, column_name="word"):
        if len(noun_list) == 0 or len(adj_list) == 0:
            return False
        elif any(adj_list.index > noun_list.index[0]):
            return adj_list[column_name][adj_list.index > noun_list.index[0]].iloc[0] in word_list

        else:
            return False


    @staticmethod
    def is_last_two_words_in(word_list, df, column_name="word"):
        return len(df) > 3 and Df_util.anything_isin(word_list, df.loc[len(df) - 2:, column_name])

    @staticmethod
    def is_first_subject_in(word_list, noun_list, verb_list):
        if len(noun_list) == 0 or len(verb_list) == 0:
            return False
        elif any(noun_list.index < verb_list.index[0]):
            return noun_list["word"][noun_list.index < verb_list.index[0]].iloc[0] in word_list
        else:
            return False

    @staticmethod
    def exist_subj_for_first_verb(noun_list, verb_list):
        if len(verb_list) == 0:
            return False
        elif any(noun_list.index < verb_list.index[0]):
            return True
        else:
            return False


    @staticmethod
    def is_verb_of_second_subject_in(word_list, verb_list, verb_idx_of_second_subject):
        if len(verb_list) == 0:
            return False
        else:
            return verb_list.loc[verb_idx_of_second_subject, "word"] in word_list

    @staticmethod
    def is_second_word_in(word_list, df, column_name="word"):
        if len(df) < 2:
            return False
        else:
            return df.loc[1, column_name] in word_list

    @staticmethod
    def is_second_words_pos_in(pos_lists, df):
        if len(df) < 2:
            return False
        else:
            return df.loc[1, "pos"] in pos_lists

    @staticmethod
    def is_second_subject_in(word_list, noun_list):
        if len(noun_list) == 0:
            return False
        else:
            return noun_list["word"].iloc[1] in word_list

    @staticmethod
    def is_second_verb_in(word_list, noun_list, verb_list):
        if len(noun_list) < 2 or len(verb_list) == 0:
            return False
        elif any(verb_list.index > noun_list.index[1]):
            return Nlp_util.get_second_verb(noun_list, verb_list) in word_list
        else:
            return False

    @staticmethod
    def is_last_word(word_list, df, column_name="word"):
        try:
            return df.iloc[len(df) - 1][column_name] in word_list
        except:
            logging.exception('')
            return False



    @staticmethod
    def is_before_first_noun(word_list, series, noun_list):
        if len(noun_list) == 0:
            return False
        else:
            return Df_util.anything_isin(word_list, series.loc[:noun_list.index[0]])

    @staticmethod
    def is_before_first_verb(word_list, series, verb_list):
        if len(verb_list) == 0:
            return False
        else:
            return Df_util.anything_isin(word_list, series.loc[:verb_list.index[0]])

    @staticmethod
    def is_before_second_verb(word_list, series, verb_list):
        if len(verb_list) == 0:
            return False
        else:
            return Df_util.anything_isin(word_list, series.loc[:verb_list.index[1]])

    @staticmethod
    def is_any_verb_before_first_noun(noun_list, verb_list):
        if len(noun_list) == 0 or len(verb_list) == 0:
            return False
        else:
            return any(noun_list.index[0] > verb_list.index)

    @staticmethod
    def is_any_verb_for_first_noun(noun_list, verb_list):
        if len(noun_list) == 0 or len(verb_list) == 0:
            return False
        elif len(noun_list) > 2:
            return any(noun_list.index[0] < verb_list.index) and any(verb_list.index < noun_list.index[1])
        else:
            return any(noun_list.index[0] < verb_list.index)


    @staticmethod
    def is_after_first_verb_in(word_list, series, first_verb_idx):
        return any(first_verb_idx < series.loc[series.isin(word_list)].index)

    @staticmethod
    def is_word_list1_after_word_list2(word1_list, word2_list, series):
        if any(series.isin(word1_list)) and any(series.isin(word2_list)):
            return any(series.loc[series.isin(word1_list)].index > series.loc[series.isin(word2_list)].index[0])
        else:
            return False

    @staticmethod
    def is_word_list1_before_word_list2(word1_list, word2_list, series):
        if Df_util.anything_isin(word1_list, series) and Df_util.anything_isin(word2_list, series):
            return any(series.loc[series.isin(word1_list)].index[0] < series.loc[series.isin(word2_list)].index)
        else:
            return False

    @staticmethod
    def is_prp_in(series):
        return any(series.isin(Nlp_util.pos_PRPs))

    @staticmethod
    def joint_have_to(df):
        if Df_util.nothing_isin(["have", "had", "has"], df.loc[:, "word"]) or Df_util.nothing_isin(["to"], df["word"]):
            return df
        dic = {'have to': 'MD', 'has to': 'MD', 'had to': 'MD'}
        have_idx_list = Nlp_util.make_idx_list_by(["have", "had", "has"], df)
        to_idx_list = Nlp_util.make_idx_list_by(["to"], df)
        # haveとtoが続く組み合わせを発見し、そのhaveの方のindexをとる。
        haveto_idx_list = Df_util.make_pair_words_idx_list(have_idx_list, to_idx_list)
        # haveとtoを合わせた１行を作り、その後indexを合わせた
        merged_df = Nlp_util.merge_pair_words_in(df, haveto_idx_list).reset_index(drop=True)
        fixed_df = Nlp_util.change_pos_of_word(merged_df, dic)
        return fixed_df

    @staticmethod
    def joint_continuous_words_by_pos(pos_list1, pos_list2, final_pos, df, exception_words={}):
        if Df_util.nothing_isin(pos_list1, df["pos"]) or Df_util.nothing_isin(pos_list2, df["pos"]):
            return df

        p1_idx_list = Nlp_util.make_idx_list_by(pos_list1, df, "pos")
        p2_idx_list = Nlp_util.make_idx_list_by(pos_list2, df, "pos")
        p1_p2_pair_idx_list = list(Df_util.make_pair_words_idx_list(p1_idx_list, p2_idx_list))
        verb_list = Nlp_util.make_verb_list(df)
        for pair_idx in p1_p2_pair_idx_list:
            if df.loc[pair_idx, "word"] in exception_words or df.loc[pair_idx + 1, "word"] in exception_words:
                p1_p2_pair_idx_list = p1_p2_pair_idx_list.remove(pair_idx)
            elif any(verb_list.index < pair_idx):
                if Nlp_util.is_last_word(Nlp_util.BE_TYPE, verb_list[verb_list.index < pair_idx]):
                    p1_p2_pair_idx_list = p1_p2_pair_idx_list.remove(pair_idx)
                else:
                    pass
            else:
                pass
        if p1_p2_pair_idx_list == None:
            return df
        merged_df = Nlp_util.merge_pair_words_in(df, list(p1_p2_pair_idx_list))
        merged_df.loc[p1_p2_pair_idx_list, "pos"] = final_pos
        return merged_df.reset_index(drop=True)

    @staticmethod
    def make_noun_list(df, tag_column="pos"):
        return df[df[tag_column].isin(Nlp_util.pos_PRPs + Nlp_util.pos_NOUNs)]

    @staticmethod
    def make_adj_list(df, tag_column="pos"):
        return df[df[tag_column].isin(Nlp_util.pos_ADJECTIVEs)]

    @staticmethod
    def make_verb_list(df, tag_column="pos", type="question"):
        noun_list = Nlp_util.make_noun_list(df)
        verb_list = df[df[tag_column].isin(Nlp_util.pos_VERBs)]
        # do youのdoは動詞とみなしたくない
        if type == "question" and len(noun_list) != 0 and Df_util.anything_isin(Nlp_util.DO_TYPE, df.loc[:noun_list.index[0], "word"]):
            first_do_type_idx = df[df.loc[:, "word"].isin(Nlp_util.DO_TYPE)].index[0]
            return verb_list.drop(first_do_type_idx)
        return verb_list


    @staticmethod
    def make_idx_list_by(word_list, df, word_column="word"):
        return df.index[df[word_column].isin(word_list)].tolist()

    @staticmethod
    def make_original_and_suited_verb(verb_list, subject_word, subject_index):
        if len(verb_list) == 0:
            return ["", ""]

        elif any(verb_list.index > subject_index):
            verb_series = verb_list.loc[subject_index:].iloc[0]
            verb_list = Nlp_util.change_verb_form(subject_word, verb_series["word"], verb_series["pos"])
            return verb_list
        elif any(verb_list.index < subject_index):
            verb_series = verb_list.loc[:subject_index].iloc[-1]
            verb_list = Nlp_util.change_verb_form(subject_word, verb_series["word"], verb_series["pos"])
            return verb_list
        else:
            return ["", ""]

    @staticmethod
    def merge_pair_words_in(df, pair_words_idx_list, word_column="word", word_idx_column="widx"):
        for i in pair_words_idx_list:
            df.loc[i, word_column] += " " + df.loc[i + 1, word_column]
            df = df.drop(i + 1)
            df.loc[i + 1:, word_idx_column] -= 1
        return df

    @staticmethod
    def reset_widx(df):
        widx_list = []
        for sidx in set(df.sidx.values):
            widx_list += range(0, len(df[df.sidx == sidx]))
        df.widx = widx_list
        return df

    @staticmethod
    def reset_sidx(df):
        sidx_list = set(df.sidx.values)
        for idx, sidx in enumerate(sidx_list):
            df.loc[df.sidx == sidx, "sidx"] = idx
        return df




