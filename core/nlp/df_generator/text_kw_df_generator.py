import logging
import pandas as pd
from common.constant.df_from_csv import KWDF, NGDF
from common.word_format.word_formatter import WordFormatter
import re
from core.nlp.response_generator.product.cct.reaction_generator import SP_I_DF


class TextKwDFGenerator:
    def __call__(self, text_df):
        w_toks = WordFormatter.Df2WToks(text_df, column_name="base_form")

        try:
            matched_list = []
            for sidx, sent in enumerate(w_toks):
                for widx, word in enumerate(sent):
                    kw_type = self.__find_keywords_from_csv(text_df, sidx, widx, word)
                    if kw_type == 'EMPHASIS':
                        matched_list.append([sidx, widx, word, 'emphasis'])
                    elif kw_type == 'KEYWORD':
                        matched_list.append([sidx, widx, word, '-'])

            if all('-' not in i for i in matched_list):
                return None
        except Exception:
            logging.exception('Error at: ' + str(__name__))
            return None

        try:
            text_kw_df = pd.DataFrame(matched_list)
            text_kw_df.columns = ['sidx', 'widx', 'word', 'Target']

            text_kw_df = self.__detect_following_emphasis(text_df, text_kw_df)
            text_kw_df = self.__detect_prior_emphasis(text_df, text_kw_df)

            text_kw_df.sort_values(['sidx', 'widx'], ascending=[True, True], inplace=True)
            text_kw_df = text_kw_df.reset_index(drop=True)

            text_kw_df = self.__add_points_text_kw_df(text_df, text_kw_df)

            return text_kw_df

        except:
            logging.exception('')
            return None

    @classmethod
    def __add_points_text_kw_df(cls, text_df, text_kw_df):
        try:
            text_kw_df['ng'] = cls.__get_matched_negative_flags(text_df, text_kw_df)
            # text_kw_df["w_type"] = text_kw_df.apply(lambda row: KWDF[KWDF.keyword == row.word].reset_index().subject,
            #                                         axis=1)
            # text_kw_df["subj"] = text_kw_df.apply(lambda row: cls.__get_subject_for_kw(row, text_df),
            #                                       axis=1)
            # text_kw_df["subj"] = text_kw_df["subj"].apply(lambda row: cls.__get_proper_subject_form(row))
            text_kw_df["iscore"] = text_kw_df.apply(lambda row: KWDF[KWDF.keyword == row.word].reset_index().score,
                                                    axis=1)
            text_kw_df["kw_type"] = text_kw_df.apply(lambda row: KWDF[KWDF.keyword == row.word].reset_index()['Type'],
                                                     axis=1)
            text_kw_df["sscore"] = text_kw_df.apply(lambda row: row.iscore * -1 if row.kw_type == "n" else row.iscore,
                                                    axis=1)
            text_kw_df = cls.__calculate_negative_keyword_score(text_kw_df)

            text_kw_df = cls.__calculate_emphasis_point(text_kw_df)

            text_kw_df["special"] = text_kw_df.apply(
                lambda row: SP_I_DF[SP_I_DF.word == row.word].id.values[
                    0] if row.word in SP_I_DF.word.tolist() else 'normal',
                axis=1)

            text_kw_df['fact'] = text_kw_df.apply(
                lambda row: True if row[2] in KWDF[KWDF.fact == 'TRUE'].keyword.values else False if row[2] in KWDF[
                    KWDF.fact == 'FALSE'].keyword.values else None, axis=1)
            return text_kw_df

        except Exception:
            logging.exception('Error at: ' + str(__name__))
            return None

    @classmethod
    def __find_keywords_from_csv(cls, text_df, sidx, widx, word):
        if word == 'like' and not cls.__is_like_verb(text_df, sidx, widx):
            return False

        if word in {'ok', 'okay'} and len(text_df[text_df.sidx == sidx]) <= 2:
            return False

        if word in KWDF[KWDF['Type'] == 'e'].keyword.values:
            return 'EMPHASIS'
        elif word in KWDF[KWDF['Type'] != 'e'].keyword.values:
            return 'KEYWORD'
        else:
            return False

    @staticmethod
    def __is_like_verb(text_df, sidx, widx):
        if text_df[(text_df.sidx == sidx) & (text_df.widx == widx)].pos.values[0] != 'IN':
            return True
        else:
            return False

    @classmethod
    def __detect_following_emphasis(cls, text_df, text_kw_df):
        # for each emphasis word, check if it emphasize words before it.
        emphasis_word_df = text_kw_df[text_kw_df.Target == 'emphasis']

        if len(emphasis_word_df) == 0:
            return text_kw_df

        kw_emp_range = emphasis_word_df.apply(
            lambda row: cls.__define_following_search_range(row, text_kw_df), axis=1)
        kw_emp_range = kw_emp_range.dropna()

        text_kw_df.iloc[kw_emp_range.index.tolist(), :] = kw_emp_range
        text_kw_df = text_kw_df.dropna()

        # only apply to emphasis that is still valid
        emphasis_to_verify = text_kw_df.iloc[text_kw_df[(text_kw_df.Target != 'emphasis') & (
                text_kw_df.Target != '-')].index.tolist(), :]

        emphasis_to_verify = emphasis_to_verify.apply(
            lambda row: cls.__verify_following_emphasized_word(row, text_kw_df, text_df), axis=1)

        text_kw_df.loc[emphasis_to_verify.index.tolist(), 'Target'] = emphasis_to_verify.Target

        return text_kw_df

    @staticmethod
    def __define_following_search_range(row, text_kw_df):
        # e.g. row is df of sidx, widx, word, Target
        target_range = text_kw_df[
            (text_kw_df.sidx == row.sidx) & (text_kw_df.widx < row.widx) & (text_kw_df.Target == '-')]

        if len(target_range) == 0:
            return row

        row.Target = target_range.widx.values[-1]

        return row

    # check if row's word(=emphasis) is for keyword or not.
    @staticmethod
    def __verify_following_emphasized_word(row, text_kw_df, text_df):
        is_next_to_keyword = len(
            text_kw_df[
                (text_kw_df.sidx == row.sidx)
                & (text_kw_df.widx == row.widx - 1)
                & (text_kw_df.Target == '-')
                ]
        ) != 0

        if is_next_to_keyword:
            row.Target = row.widx - 1
            return row

        target_sidx = row.sidx
        upper_end = row.Target + 1
        bottom_end = row.widx - 1

        kw_emp_range_df = text_df[
            (text_df.sidx == target_sidx) & (text_df.widx >= upper_end) & (text_df.widx <= bottom_end)]

        for idx in reversed(kw_emp_range_df.index):
            # if you find pos in the dict, then stop verifying
            pos_to_verify = text_df.loc[idx, 'pos']
            word_to_verify = text_df.loc[idx, 'word']

            if pos_to_verify in {'CC', 'NNP', 'NN', 'WP', 'IN'} or word_to_verify == ',':
                row.Target = 'emphasis'
                return row
            elif idx == kw_emp_range_df.index.tolist()[0]:
                # emphasized keyword found!!
                # row.Target has to be the widx of emphasized keyword
                row.Target = text_kw_df[(text_kw_df.sidx == row.sidx) & (text_kw_df.widx < row.widx) & (
                        text_kw_df.Target == '-')].widx.values[-1]
                return row

    @classmethod
    def __detect_prior_emphasis(cls, text_df, text_kw_df):
        emphasis_word_df = text_kw_df[text_kw_df.Target == 'emphasis']

        if len(emphasis_word_df) == 0:
            return text_kw_df

        # find a range to verify
        emp_kw_range = emphasis_word_df.apply(
            lambda row: cls.__define_prior_search_range(row, text_kw_df),
            axis=1
        )

        emp_kw_range = emp_kw_range.dropna()

        # drop emphasis which are not followed by keywords
        # e.g. i am so sad and I don't know very much -> 'very', 'much' will be droped
        if not all(type(i) != str for i in emp_kw_range.Target.values):
            emphasis_to_verify = emp_kw_range[emp_kw_range.Target != 'emphasis']
        else:
            emphasis_to_verify = emp_kw_range
        emphasis_verified = emphasis_to_verify.apply(
            lambda row: cls.__verify_prior_emphasized_word(row, text_kw_df, text_df), axis=1
        )

        text_kw_df.loc[emphasis_verified.index.tolist(), 'Target'] = emphasis_verified.Target
        text_kw_df = text_kw_df[(text_kw_df.Target != 'not found') & (text_kw_df.Target != 'emphasis')]

        return text_kw_df

    @staticmethod
    def __define_prior_search_range(row, text_kw_df):
        target_range = text_kw_df[
            (text_kw_df.sidx == row.sidx) & (text_kw_df.widx > row.widx) & (text_kw_df.Target == '-')]

        if len(target_range) == 0:
            return row

        row.Target = target_range.widx.values[0]

        return row

    @staticmethod
    def __verify_prior_emphasized_word(row, text_kw_df, text_df):
        is_next_to_kw = len(text_kw_df[(text_kw_df.sidx == row.sidx) & (text_kw_df.widx == row.widx + 1) & (
                text_kw_df.Target == '-')]) != 0
        if is_next_to_kw:
            row.Target = row.widx + 1
            return row

        target_sidx = row.sidx
        begin = row.widx + 1
        end = row.Target - 1

        emp_kw_range_df = text_df[(text_df.sidx == target_sidx) & (text_df.widx >= begin) & (text_df.widx <= end)]

        for idx, i in emp_kw_range_df.iterrows():
            if i.pos in ['CC', 'NNP', 'NN', 'WP', 'IN'] or i.word == ',':
                row.Target = 'not found'
                return row
            elif idx == emp_kw_range_df.index[-1]:
                # emphasized keyword found!!
                row.Target = text_kw_df[(text_kw_df.sidx == row.sidx) & (text_kw_df.widx > row.widx) & (
                        text_kw_df.Target == '-')].widx.values[0]
                return row

    # <End of detecting emphasis>

    @staticmethod
    def __detect_exceptional_words(s, *re_list):
        for r in re_list:
            if r.match(s):
                return True
        return False

    @staticmethod
    def __detect_subject_normal(row, text_df):
        row_idx = text_df[(text_df.sidx == row.sidx) & (text_df.widx == row.widx)].index[0]

        fd = text_df[:row_idx].iloc[::-1]
        for idx, fd_row in fd.iterrows():
            if fd_row.pos in {"PRP", "NNP"}:
                return_value = fd_row.word
            elif fd_row.pos in {"CC", "IN", ".", ","}:
                return_value = None
            else:
                return_value = 'pass'

            if return_value != 'pass':
                return return_value

        return None

    @staticmethod
    def __detect_subj_surprise(text_df):
        for idx, row in text_df.iterrows():
            if row.pos in {"PRP"} or row.pos in {"guy", "person", "friend", "buddy", "man", "girl"}:
                result = row.word
            elif row.pos in {"CC", ".", ","}:
                result = None
            else:
                result = 'pass'

            if result != 'pass':
                return result

        return None

    @staticmethod
    def __detect_subj_hurt(row, text_df):
        for idx, df_row in text_df.iterrows():
            if df_row.pos in {"PRP"} or df_row["pos"] in {"guy", "person", "friend", "buddy", "man", "girl"}:
                return df_row.word
            elif df_row.pos in ("CC", 'IN', ".", ","):
                break

        num = text_df[(text_df.sidx == row.sidx) & (text_df.widx == row.widx)].index[0]

        fd = text_df[:num].iloc[::-1]
        for idx, fd_row in fd.iterrows():
            if fd_row.pos in {"PRP", "NN"}:
                result = fd_row.word
            elif fd_row.pos in {"CC", 'IN', ".", ","}:
                result = None
            else:
                result = 'pass'

            if result != 'pass':
                return result

        return None

    @classmethod
    def __get_subject_for_kw(cls, row, text_df):
        # find PRP or NN before the word
        # find PRP or personal pronoun after the word
        # find PRP or oersonal pronoun after the word then find PRP or NN before the word
        if row.w_type == "normal":
            return cls.__detect_subject_normal(row, text_df)
        elif row.w_type == "surprise":
            return cls.__detect_subj_surprise(text_df)
        elif row.w_type == "hurt":
            return cls.__detect_subj_hurt(row, text_df)

    @staticmethod
    def __get_proper_subject_form(row):
        proper_change = {
            "him": "he",
            "them": "they",
            "us": "we",
            "her": "she",
            "me": "i",
            "this": "that",
            "these": "those",
        }
        if row in proper_change.keys():
            return proper_change[row]

        return row

    @staticmethod
    def __ng_check(row):
        return True if row.word in NGDF.negative.values else False

    @classmethod
    def __get_matched_negative_flags(cls, text_df, text_kw_df):
        # detect word by NGDF list
        text_df = text_df
        text_df['ng_kw'] = text_df.apply(lambda r: cls.__ng_check(r), axis=1)

        re_list = [
            re.compile(r"^PRP$"),
            re.compile(r"\."),
            re.compile(r","),
        ]
        ng = []
        num_ng = []

        # loop each kws and reverse text_df[:kw_idx]
        for idx, row in text_kw_df.iterrows():
            if row.Target != '-':
                ng.append(False)
                continue

            num = text_df[(text_df.sidx == row.sidx) & (text_df.widx == row.widx)].index[0]

            fd = text_df[:num].iloc[::-1]

            for w_idx, w_row in fd.iterrows():
                if w_row.ng_kw:
                    num_ng.append(True)
                elif cls.__detect_exceptional_words(w_row.pos, *re_list):
                    break
            # detect double negative
            ng.append(False) if not (len(num_ng) > 0 and len(num_ng) % 2 != 0) else ng.append(True)
            num_ng = []

        return ng

    @staticmethod
    def __calculate_emphasis_point(text_kw_df):
        # make a df of emphasis words from text_kw_df where Target is not Unknown
        emphasis_words_df = text_kw_df[text_kw_df.Target != '-']

        for idx, row in emphasis_words_df.iterrows():
            text_kw_df.loc[
                text_kw_df[(text_kw_df.sidx == row.sidx) & (text_kw_df.widx == row.Target)].index, ['iscore', 'sscore']
            ] *= row.iscore

        text_kw_df = text_kw_df[text_kw_df.Target == '-'].reset_index(drop=True)

        return text_kw_df

    @staticmethod
    def __calculate_negative_keyword_score(text_kw_df):
        # set the magic number for negative keyword
        magic_num = 5000

        # calculate sentiment of each word depending on if negative or not
        text_kw_df.sscore = text_kw_df.apply(
            lambda row: row.sscore if not row['ng'] else -1 / row['sscore'] * magic_num, axis=1)

        return text_kw_df
