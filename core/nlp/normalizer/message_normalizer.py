import logging
from typing import List, Dict

from common.util.util import send_typing_on
from core.nlp.df_generator.original_df_generator import OriginalDFGenerator
from common.constant.df_from_csv import STICKER_DF, SFDF, WANNA_SHORT_FORM, UNIMPORTANT_WORDS_FOR_REPEAT
from core.nlp.question import question
from common.word_format.word_formatter import WordFormatter
from nltk import word_tokenize
from common.word_format.df_utils import Nlp_util


class MessageNormalizer:
    def __call__(self, message_dicts: List[Dict[str, str]], sender_id, from_preprocessor=True):
        try:
            if from_preprocessor:
                message_dicts = self.__convert_attachment(message_dicts)

                message_dicts = self.__normalize_apostrophe(message_dicts)

                w_toks = WordFormatter.MsgDict2WToks(message_dicts)
            else:
                w_toks = message_dicts

            print('\nword_tokenized\n', w_toks)

            normalized_w_toks = self.normalize_message_by_w_toks(w_toks)

            send_typing_on(sender_id)

            # make original_df with sidx, widx, word, pos tag
            df = OriginalDFGenerator.create_original_df_by_w_toks(normalized_w_toks)

            df = self.normalize_message_by_df(df)

            return df
        except:
            logging.exception('')
            return None

    def normalize_message_by_w_toks(self, w_toks):
        # [[], [], []]
        w_toks = self.__lowercase_w_toks(w_toks)

        w_toks = self.__correct_short(w_toks)

        w_toks = self.__remove_stickers(w_toks)

        w_toks = self.__correct_end_symbol(w_toks)

        return w_toks

    @classmethod
    def normalize_message_for_question(cls, w_toks):
        # [[], [], []]
        w_toks = cls.__normalize_apostrophe(w_toks)
        w_toks = cls.__lowercase_w_toks(w_toks)
        w_toks = cls.__remove_stickers(w_toks)
        w_toks = cls.__remove_exceptional_stop_words(w_toks)

        return w_toks

    # format original text
    @staticmethod
    def __lowercase_w_toks(w_toks):
        try:
            w_toks = [[w.lower() for w in s] for s in w_toks]

            return w_toks
        except:
            logging.exception('')
            return w_toks

    @staticmethod
    def __lowercase_by_pos(row):
        if row.pos != 'NNP':
            row.word = row.word.lower()

        return row

    @classmethod
    def __correct_short(cls, w_toks):
        try:
            w_toks = cls.__correct_prp_short_form(w_toks)

            w_toks = cls.__correct_wanna_type_abbreviations(w_toks)

            text = WordFormatter.WToks2Str(w_toks)

            # remove ' because it make word_tokenize messy
            text = text.replace('\'', '')

            w_toks = WordFormatter.Str2WToks(text)

            corrected_w_toks = []
            for sent in w_toks:
                corrected_w_toks.append([])

                for idx, word in enumerate(sent):

                    if word in SFDF.short.values:
                        w_tokenized_replacement = word_tokenize(SFDF[SFDF.short == word].normal.values[0])

                        for replacement_word in w_tokenized_replacement:
                            corrected_w_toks[-1] = corrected_w_toks[-1] + [replacement_word]
                    elif idx == 0 and word == "cause":
                        corrected_w_toks[-1] = corrected_w_toks[-1] + ["because"]

                    else:
                        corrected_w_toks[-1] = corrected_w_toks[-1] + [word]

            return corrected_w_toks
        except:
            logging.exception('')
            return w_toks

    @classmethod
    def __correct_prp_short_form(cls, w_toks):
        try:
            short = ["'d", "'ll", "'m", "'re", "'s", "'ve", "it's", "n't"]
            count = 0

            while any(w in short for s in w_toks for w in s):
                w_toks = cls.__replace_prp_short(w_toks, short)
                count += 1

                if count > 25:
                    return w_toks

            return w_toks
        except:
            logging.exception('')
            return w_toks

    @classmethod
    def __replace_prp_short(cls, w_toks, short):
        try:
            for sidx, s in enumerate(w_toks):
                for widx, w in enumerate(s):
                    if w in short:
                        if w == short[0]:
                            w_toks = cls.correct_short_d(w_toks, sidx, widx)
                        elif w == short[1]:
                            w_toks = cls.correct_short_ll(w_toks, sidx, widx)
                        elif w == short[2]:
                            w_toks = cls.correct_short_m(w_toks, sidx, widx)
                        elif w == short[3]:
                            w_toks = cls.correct_short_re(w_toks, sidx, widx)
                        elif w == short[4]:
                            w_toks = cls.correct_short_s(w_toks, sidx, widx)
                        elif w == short[5]:
                            w_toks = cls.correct_short_ve(w_toks, sidx, widx)
                        elif w == short[6]:
                            w_toks = cls.correct_short_its(w_toks, sidx, widx)
                        elif w == short[7]:
                            w_toks = cls.correct_short_nt(w_toks, sidx, widx)
                        return w_toks
        except:
            logging.exception('')
            return w_toks

    @classmethod
    def correct_short_d(cls, w_toks, sidx, widx):
        try:
            w_toks[sidx][widx] = 'would'

            return w_toks
        except:
            logging.exception("")
            return w_toks

    @classmethod
    def correct_short_ll(cls, w_toks, sidx, widx):
        try:
            w_toks[sidx][widx] = 'will'

            return w_toks
        except:
            logging.exception('')
            return w_toks

    @classmethod
    def correct_short_m(cls, w_toks, sidx, widx):
        try:
            w_toks[sidx][widx] = 'am'
            return w_toks
        except:
            logging.exception('')
            return w_toks

    @classmethod
    def correct_short_re(cls, w_toks, sidx, widx):
        try:
            w_toks[sidx][widx] = 'are'
            return w_toks
        except:
            logging.exception('')
            return w_toks

    @classmethod
    def correct_short_s(cls, w_toks, sidx, widx):
        try:
            prior = ['he', 'she', 'that', 'it', 'what', 'where', 'which', 'who', 'how', 'when', 'there', 'why']
            if w_toks[sidx][widx - 1] in prior:
                w_toks[sidx][widx] = 'is'
            else:
                w_toks[sidx][widx - 1] = w_toks[sidx][widx - 1] + "'s"
                w_toks[sidx][widx] = ''

            return w_toks
        except:
            logging.exception('')
            return w_toks

    @classmethod
    def correct_short_ve(cls, w_toks, sidx, widx):
        try:
            w_toks[sidx][widx] = 'have'
            return w_toks
        except:
            logging.exception('')
            return w_toks

    @classmethod
    def correct_short_its(cls, w_toks, sidx, widx):
        try:
            w_toks[sidx][widx] = 'it'
            w_toks[sidx].insert(widx + 1, 'is')

            return w_toks
        except:
            logging.exception('')
            return w_toks

    @classmethod
    def correct_short_nt(cls, w_toks, sidx, widx):
        try:
            if w_toks[sidx][widx - 1] == 'ca':
                w_toks[sidx][widx - 1] = 'can'
            elif w_toks[sidx][widx - 1] == 'wo':
                w_toks[sidx][widx - 1] = 'will'

            w_toks[sidx][widx] = 'not'

            return w_toks
        except:
            logging.exception('')
            return w_toks

    @staticmethod
    def __correct_wanna_type_abbreviations(w_toks):
        try:
            for sidx, sent in enumerate(w_toks):
                for short in set(WANNA_SHORT_FORM.short):
                    target_row = WANNA_SHORT_FORM[WANNA_SHORT_FORM.short == short]
                    while short in sent:
                        short_idx = sent.index(short)

                        prior_word_list = target_row.prior.tolist()

                        if sent[short_idx - 1] in prior_word_list:
                            sent[short_idx - 1] = target_row[
                                target_row.prior == sent[short_idx - 1]
                                ].replacement1.values[0]

                            sent[short_idx] = target_row.replacement2.values[0]
                        else:
                            sent[short_idx] = 'no'

                w_toks[sidx] = sent

            return w_toks
        except:
            logging.exception('')
            return w_toks

    @staticmethod
    def __remove_stickers(w_toks):
        try:
            for sidx, s in enumerate(w_toks):
                s_text = WordFormatter.SingleWToks2Str(s)

                for i in STICKER_DF.sticker.tolist():
                    while i in s_text:
                        first = s_text[:s_text.index(i)]
                        last = s_text[s_text.index(i) + len(i):]

                        s_text = first + last

                new_w_tok = word_tokenize(s_text)
                w_toks[sidx] = new_w_tok

            return w_toks
        except:
            logging.exception('')
            return w_toks

    @classmethod
    def cut_sent_by_unimportant_words_at_head(cls, df):
        try:
            fixed_df = df
            while len(fixed_df) != 0:
                is_fixed_df_modified = False

                for sidx in set(fixed_df.sidx):
                    if len(fixed_df[fixed_df.sidx == sidx]) == 1:
                        continue

                    head_row = fixed_df[fixed_df.sidx == sidx].iloc[0]
                    head_word = head_row.word

                    if head_word in UNIMPORTANT_WORDS_FOR_REPEAT.word.values:
                        fixed_df.loc[fixed_df.index > head_row.name, "sidx"] += 1
                        fixed_df = Nlp_util.reset_widx(fixed_df)

                        is_fixed_df_modified = True
                        break
                    elif not head_word.isalpha():
                        if not head_word.isdigit():
                            fixed_df = cls.__remove_nums_n_symbols(fixed_df, sidx)
                            is_fixed_df_modified = True
                            break

                if not is_fixed_df_modified:
                    break

            return fixed_df
        except:
            logging.exception('')
            return df

    @classmethod
    def __remove_nums_n_symbols(cls, fixed_df, sidx):
        try:
            fixed_df = fixed_df.drop(fixed_df[fixed_df.sidx == sidx].iloc[0].name)
            fixed_df = fixed_df.reset_index(drop=True)
            fixed_df.loc[fixed_df.sidx == sidx] = Nlp_util.reset_widx(fixed_df.loc[fixed_df.sidx == sidx])

            return fixed_df
        except:
            logging.exception('')
            return fixed_df

    @staticmethod
    def remove_unimportant_words_at_tail(df):
        try:
            for sidx in set(df.sidx.values):
                while len(df.loc[df.sidx == sidx]) != 1:
                    tail_row = df.loc[((df.sidx == sidx) & (df.widx == len(df[df.sidx == sidx]) - 1))]
                    tail_word = tail_row.word.values[0]
                    if tail_word in list(UNIMPORTANT_WORDS_FOR_REPEAT.word.values) + [","]:
                        if tail_word == 'well':
                            if tail_row.widx.values[0] > len(df[df.sidx == tail_row.sidx.values[0]]) / 2:
                                break

                        df = df.drop(tail_row.index[0])
                        df = Nlp_util.reset_widx(df)
                    else:
                        break

            df = df.reset_index(drop=True)
            return df
        except:
            logging.exception('')
            return df

    @classmethod
    def cut_sent_by_interjection(cls, df):
        try:
            separators = [",", "and", "but", "or", "then", "so", "plus", "cause", "because"]

            exists_separator = True

            while exists_separator:
                separators_in_message = df[(df.word.isin(separators)) & (df.widx != 0)]

                if separators_in_message.empty:
                    exists_separator = False
                else:
                    for idx, separator in separators_in_message.iterrows():
                        if separator.word == 'so' and separator.pos == 'RB':
                            continue
                        elif separator.word == 'cause' and separator.pos != 'VB':
                            continue

                        if cls.__exists_SV_around_cc(df, separators_in_message, separator):
                            df.loc[df[(df.sidx >= separator.sidx) & (df.index >= idx)].index, "sidx"] += 1
                            df = Nlp_util.reset_widx(df)
                            break
                    else:
                        exists_separator = False
            return df
        except:
            logging.exception('')
            return df

    @classmethod
    def __exists_SV_around_cc(cls, df, cc_in_message, cc):
        try:
            sent_with_cc = df[df.sidx == cc.sidx]

            nouns_in_sent = Nlp_util.make_noun_list(sent_with_cc)
            verbs_in_sent = Nlp_util.make_verb_list(sent_with_cc, type="normal")

            first_half_of_sent = sent_with_cc[sent_with_cc.widx < cc.widx]
            nouns_in_first_half = nouns_in_sent[(nouns_in_sent.sidx == cc.sidx) & (nouns_in_sent.widx < cc.widx)]
            verbs_in_first_half = verbs_in_sent[(verbs_in_sent.sidx == cc.sidx) & (verbs_in_sent.widx < cc.widx)]

            other_cc_sidx = cc_in_message[(cc_in_message.sidx == cc.sidx) & (cc_in_message.widx > cc.widx)].sidx
            exists_other_cc_in_same_sentence = any(i == cc.sidx for i in other_cc_sidx)

            if exists_other_cc_in_same_sentence:
                other_cc_widx = cc_in_message[cc_in_message.index > cc.widx].index[0]
            else:
                other_cc_widx = len(sent_with_cc)

            second_half_of_sent = sent_with_cc[(sent_with_cc.widx >= cc.widx) & (sent_with_cc.widx < other_cc_widx)]

            if cls.__is_finishing_with_question_mark(second_half_of_sent):
                second_half_of_sent = second_half_of_sent.iloc[:-1]

            nouns_in_second_half = cls.__get_second_half_words(nouns_in_sent, cc, other_cc_widx)
            verbs_in_second_half = cls.__get_second_half_words(verbs_in_sent, cc, other_cc_widx)

            return cls.__is_complete_sent(nouns_in_first_half, verbs_in_first_half, first_half_of_sent) and \
                   cls.__is_complete_sent(nouns_in_second_half, verbs_in_second_half, second_half_of_sent)
        except:
            logging.exception('')
            return False

    @staticmethod
    def __is_complete_sent(nouns, verbs, sent):
        return Nlp_util.exists_any_noun_verb_pair(nouns, verbs) \
               or question.DetectQuestion.is_question_form(sent, nouns, verbs)

    @staticmethod
    def __get_second_half_words(df, cc, other_cc_widx):
        second_half_words = df[(df.widx >= cc.widx) & (df.widx < other_cc_widx)]
        return second_half_words

    @staticmethod
    def __is_finishing_with_question_mark(second_half_of_sent):
        return second_half_of_sent.iloc[-1].word == "?"

    # correct '...' or '!!' to '.'
    @staticmethod
    def __correct_end_symbol(w_toks):
        try:
            for sidx, sent in enumerate(w_toks):
                if len(sent) != 0:
                    # on the condition of that sent with ? always get question as intent.
                    while all(c != "?" and not (c.isalpha() or c.isdigit()) for c in sent[-1]):
                        sent = sent[:-1]

                        if len(sent) == 0:
                            w_toks[sidx] = sent
                            break

                    w_toks[sidx] = sent

            return w_toks
        except:
            logging.exception('')
            return w_toks

    # >>>>>>>>> After getting intents
    @staticmethod
    def __remove_unimportant_intent_sent(w_toks, intents):
        keeping_intent_list = ['normal', 'question']

        try:
            # if 'normal' or 'question' not in self.intents:
            if not any(i in keeping_intent_list for i in intents):
                return None

            new_w_toks = []
            # remove unimportant intent sentence from w_toks
            for i, w in zip(intents, w_toks):
                if i in keeping_intent_list:
                    new_w_toks.append(w)

            return new_w_toks
        except:
            logging.exception('')
            return w_toks

    @staticmethod
    def __remove_exceptional_stop_words(w_toks):
        # remove words like yessssss
        return w_toks

    @classmethod
    def __normalize_apostrophe(cls, message_dicts):
        try:
            message_dicts = [{'text': i['text'].replace("’", "'"), 'id': i['id']} for i in message_dicts]
            return message_dicts
        except:
            logging.exception('')
            return message_dicts

    def normalize_message_by_df(self, df):
        try:
            if df is None:
                return None

            df = MessageNormalizer.cut_sent_by_interjection(df)

            df = MessageNormalizer.cut_sent_by_unimportant_words_at_head(df)

            df = MessageNormalizer.remove_unimportant_words_at_tail(df)

            return df
        except:
            logging.exception('')
            return df

    def __convert_attachment(self, message_dicts):
        return [{'text': '', 'id': message['id']} if message['text'] == 'ATTACHMENT' else message for message in
                message_dicts]
