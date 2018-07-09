from pandas import DataFrame
from typing import List

from common.constant.df_from_csv import STOP_WORD_LIST, STICKER_DF
from common.constant.intent_type import Intent
from core.nlp.question import question
from common.dialogflow.dialogflow import request_to_apiai
import logging
from common.word_format.df_utils import Nlp_util, Df_util


class IntentChecker:
    def __call__(self, text_df: DataFrame):
        intent_list = []
        try:
            if text_df is None:
                return [Intent.MEANINGLESS]

            if len(text_df) > 60:
                intent_list.append(Intent.LONG_MSGs)
            sidx_list = set(text_df.sidx.values)

            for sidx in sidx_list:
                df_by_sentence = text_df[text_df.sidx == sidx].reset_index(drop=True)

                tmp = None
                try:
                    tmp = question.DetectQuestion(df_by_sentence)
                    is_question = question.DetectQuestion.is_question_form(tmp.df, tmp.noun_list, tmp.verb_list)
                except:
                    logging.exception('')
                    is_question = False

                try:

                    if self.__is_no_idea(df_by_sentence):
                        intent_list.append(Intent.NO_IDEA)

                    elif is_question:
                        question_type = question.DefineQuestionType(tmp.df).categorize_by_leading_word()
                        intent_list.append(Intent(question_type.class_name))

                    elif self.__cant_get_attention_from_bf(df_by_sentence):
                        intent_list.append(Intent.CANT_GET_ATTENTION_FROM_BF)

                    elif self.__like_someone(df_by_sentence):
                        intent_list.append(Intent.LIKE_SOMEONE)

                    elif self.__is_about_breakup(df_by_sentence):
                        intent_list.append(Intent.ABOUT_BREAKUP)

                    elif self.__is_complaint_or_dissing(df_by_sentence):
                        intent_list.append(Intent.COMPLAINT_OR_DISSING)

                    elif self.__is_meaningless_sent(df_by_sentence):
                        intent_list.append(Intent.MEANINGLESS)

                    elif self.__lack_of_confidence(df_by_sentence):
                        intent_list.append(Intent.LACK_OF_CONFIDENCE)

                    elif self.__is_call_jullie_intent(df_by_sentence):
                        intent_list.append(Intent.CALL_JULLIE)

                    elif self.__is_sticker_intent(df_by_sentence):
                        intent_list.append(Intent.STICKER)

                    elif self.__is_repeatitive(df_by_sentence):
                        intent_list.append(Intent.HATE_REPETITIVE)

                    elif self.__is_jullie_useless(df_by_sentence):
                        intent_list.append(Intent.JULLIE_USELESS)


                    elif self.__is_need_help(df_by_sentence):
                        intent_list.append(Intent.NEED_HELP)

                    elif self.__mean_no_friends(df_by_sentence):
                        intent_list.append(Intent.NO_FRIENDS)

                    elif self.__is_anxious(df_by_sentence):
                        intent_list.append(Intent.ANXIOUS)

                    elif self.__is_lonely(df_by_sentence):
                        intent_list.append(Intent.LONELY)

                    elif self.__is_call_me_names(df_by_sentence):
                        intent_list.append(Intent.CALL_ME_NAMES)

                    elif self.__is_about_money(df_by_sentence):
                        intent_list.append(Intent.MONEY)

                    elif self.__is_about_missing(df_by_sentence):
                        intent_list.append(Intent.MISSING)
                    else:
                        intent_list.append(request_to_apiai(df_by_sentence))
                except:
                    logging.exception('')

            return intent_list
        except:
            logging.exception('')
            return intent_list

    @classmethod
    def __mean_no_friends(cls, df):
        try:
            exists_nobody_likes_me = Nlp_util.are_words1_words2_words3_in_order(df, ["nobody", "no one"],
                                                                                ["like", "love"], ["me"])
            exists_friends_dont_like_me = Nlp_util.are_words1_words2_words3_in_order(df, ["friend", "they",
                                                                                          "everybody"],
                                                                                     ["not like", "not love",
                                                                                      "hate"], ["me"])

            exists_have_no_friend = Nlp_util.are_words1_words2_words3_in_order(df, ["i"],
                                                                               ["not have", "have no"],
                                                                               ["friend"])

            if exists_nobody_likes_me or exists_friends_dont_like_me or exists_have_no_friend:
                return True
            else:
                return False
        except:
            logging.exception('')
            return False

    @classmethod
    def __is_about_breakup(cls, df):
        df_ex_adverb = df[~df.pos.isin(Nlp_util.pos_ADVERBs)]
        target_list = [
            [["i", "we", "boyfriend", "girlfriend"], ["brokeup", "broke up", "did breakup", "did breakup"], []],
            [["she", "he", "boyfriend", "girlfriend", ], ["brokeup", "broke up", "did breakup", "did breakup"],
             ["with me"]],
        ]
        return any(
            Nlp_util.are_words1_words2_words3_in_order(df_ex_adverb, target[0], target[1], target[2],
                                                       df_column="word") for target
            in target_list)

    @classmethod
    def __like_someone(cls, df):
        df_ex_adverb = df[~df.pos.isin(Nlp_util.pos_ADVERBs)]
        target_list = [
            {"subjects": ["guy", "friend", "boy", "man"], "word1": ["i"], "word2": ["like"], "exceptions": []},
            {"subjects": ["i"], "word1": ["like"], "word2": ["guy", "friend", "boy", "man"],
             "exceptions": ["feel like"]},
            {"subjects": ["i"], "word1": ["be", "fall"], "word2": ["in love"], "exceptions": []}
        ]
        return any(
            Nlp_util.are_words1_words2_words3_in_order(df_ex_adverb, target["subjects"], target["word1"],
                                                       target["word2"], exception_list=target["exceptions"]) for
            target
            in target_list)

    @classmethod
    def __lack_of_confidence(cls, df):
        df_ex_adverb = df[~df.pos.isin(Nlp_util.pos_ADVERBs)]
        target_list = [
            [["i"], ["hate", "not like"], ["myself"]],
            [["i"], ["be"], ["fat", "whore", "slut", "bitch", "stupid", "ugly", "burden"]],
            [["i"], ["bother"], ["people", "everyone", "friends"]],
        ]
        return any(
            Nlp_util.are_words1_words2_words3_in_order(df_ex_adverb, target[0], target[1], target[2],
                                                       exception_list=["say", "tell"]) for target
            in target_list) or Nlp_util.are_words1_words2_words3_in_order(df, ["i"], ["be"], ["not good enough"])

    @classmethod
    def __cant_get_attention_from_bf(cls, df):
        df_ex_adverb = df[~df.pos.isin(Nlp_util.pos_ADVERBs)]
        target_list = [
            [["he", "boyfriend"], ["not pay", "never pay", "not give me", "never give me"], ["attention"]],
            [["he", "boyfriend"],
             ["not respond", "never respond", "not reply", "never reply", "not answer", "never answer", "not call",
              "never call", "not text", "never text"], []],
            [["he", "boyfriend"], ["not listen", "never listen", "not care", "never care"], ["me"]]
        ]
        return any(
            Nlp_util.are_words1_words2_words3_in_order(df_ex_adverb, target[0], target[1], target[2]) for target
            in target_list)

    @classmethod
    def __is_no_idea(cls, df):
        try:
            df_ex_adverb = df[~df.pos.isin(Nlp_util.pos_ADVERBs)]
            noun_list = Nlp_util.make_noun_list(df)
            verb_list = Nlp_util.make_verb_list(df, type="normal")
            is_subj_himself = Nlp_util.is_first_subject_in(["i"], noun_list, verb_list)
            exist_subj_for_first_verb = Nlp_util.exist_subj_for_first_verb(noun_list, verb_list)

            is_idk_what_to_do = Df_util.anything_isin({"do not know", "not sure", "have no idea"},
                                                      df_ex_adverb["base_form"]) and Df_util.anything_isin(
                {"what to do", "how to do", "what to deal", "how to deal"}, df_ex_adverb["base_form"])

            is_want_advice = Df_util.anything_isin({"want", "need", "give me"},
                                                   df_ex_adverb["base_form"]) and Df_util.anything_isin(
                {"advice", "suggestion"}, df_ex_adverb["word"])

            is_give_me_advice = Df_util.anything_isin({"need", "want", "give me"},
                                                      df_ex_adverb["base_form"]) and Df_util.anything_isin(
                {"advice", "suggestion"}, df_ex_adverb["word"])

            what_should_i_do = Nlp_util.are_words1_words2_words3_in_order(df_ex_adverb, ["what"], ["should"], ["i"])

            return (is_subj_himself and (is_idk_what_to_do or is_want_advice)) or (
                    not exist_subj_for_first_verb and is_give_me_advice) or what_should_i_do

        except Exception:
            logging.exception('Error at: ' + str(__name__))
            return False

    @staticmethod
    def __is_complaint_or_dissing(df):
        try:
            noun_list = Nlp_util.make_noun_list(df)
            verb_list = Nlp_util.make_verb_list(df, type="normal")
            said_you_dont_listen = Nlp_util.is_first_subject_in(["you"], noun_list,
                                                                verb_list) and Df_util.anything_isin(
                ["not listen", "never listen"], df["base_form"])
            is_dissing = Df_util.anything_isin(["fuck you", "hate you"], df["base_form"])

            return said_you_dont_listen or is_dissing
        except:
            logging.exception('')
            return False

    @staticmethod
    def __is_repeatitive(df):
        try:
            if df is None:
                return False

            is_repeat_in_message = any(df["base_form"].isin(["repeat"]))
            if is_repeat_in_message:
                repeat_idx = df[df["base_form"].isin(["repeat"])].index[0]

                is_you_in_message = any(df.loc[:repeat_idx, "word"].isin(["you"]))
                if is_you_in_message:
                    return True

            return False
        except:
            logging.exception('')
            return False

    @staticmethod
    def __is_jullie_useless(df):
        try:
            if df is None:
                return False

            is_useless = Nlp_util.are_words1_words2_words3_in_order(df, ["you", "this"], ["be not", "be never"],
                                                                    ["helpful", "help",
                                                                     "helping"]) or Nlp_util.are_words1_words2_words3_in_order(
                df, ["you"], ["be"],
                ['useless', 'helpless'])

            return is_useless
        except:
            logging.exception('')
            return False

    @staticmethod
    def __is_meaningless_sent(df):
        try:
            if df is None:
                return True

            return all(df["word"].isin(STOP_WORD_LIST.word.tolist()))
        except:
            logging.exception('')
            return False

    @staticmethod
    def __is_call_jullie_intent(df):
        try:
            call_jullie_words = ['jullie', 'Jullie', 'julie', 'Julie', 'J', 'j', 'Jul', 'jul', 'JJ', 'jj']

            return all(df["word"].isin(call_jullie_words + STOP_WORD_LIST.word.tolist()))
        except:
            logging.exception('')
            return False

    @staticmethod
    def __is_sticker_intent(df):
        try:
            return all(df["word"].isin(STICKER_DF.sticker.tolist()))
        except:
            logging.exception('')
            return False

    @classmethod
    def __is_not_listening(cls, df):
        try:
            if df is None:
                return False

            row_with_listen = df[df.base_form == 'listen']
            if row_with_listen.empty:
                return False
            else:
                words_before_listening = df.loc[:row_with_listen.index[0], "word"]

                exists_you_before_listen = any(words_before_listening.isin(["you"]))
                exists_negation_before_listen = any(words_before_listening.isin(['no', 'never', 'not']))

                return exists_you_before_listen and exists_negation_before_listen
        except:
            logging.exception('')
            return False

    @classmethod
    def __is_need_help(cls, df_by_sentence):
        try:
            help_in_msg = df_by_sentence[df_by_sentence.word == 'help']
            need_in_msg = df_by_sentence[df_by_sentence.word == 'need']
            return len(help_in_msg) != 0 and len(need_in_msg) != 0
        except:
            logging.exception("")
            return False

    @classmethod
    def __is_anxious(cls, df_by_sentence: DataFrame):
        try:
            word1_1 = ['anxious']
            word1_2 = ['be', 'being', 'am', 'was', 'been', 'feel', 'feeling']

            word2_1 = ['anxiety']
            word2_2 = ['have', 'having', 'had', 'feel', 'feeling']

            return Nlp_util.are_words1_words2_words3_in_order(df_by_sentence, word1_1, word1_2) \
                   or Nlp_util.are_words1_words2_words3_in_order(df_by_sentence, word2_1, word2_2)
        except:
            logging.exception('')
            return False

    @classmethod
    def __is_lonely(cls, df_by_sentence: DataFrame):
        try:
            lonely_word = 'lonely'
            all_words = df_by_sentence.word.values

            if lonely_word in all_words:
                lonely_widx = df_by_sentence[df_by_sentence.word == lonely_word].widx.values[0]

                if 'i' in all_words[:lonely_widx]:
                    return True

            return False
        except:
            logging.exception('')
            return False

    @classmethod
    def __is_call_me_names(cls, df_by_sentence):
        try:
            word1 = ['call']
            word2 = ['me']
            word3 = ['names']

            return Nlp_util.are_words1_words2_words3_in_order(df_by_sentence, word1, word2, word3)
        except:
            logging.exception('')
            return False

    @classmethod
    def __is_phrase_in_words(cls, phrase: List[str], words: List[str]):
        try:
            for i in reversed(phrase):
                if i in words:
                    widx = words.index(i)
                    words = words[:widx]
                else:
                    return False

            return True
        except:
            logging.exception('')
            return False

    @classmethod
    def __is_about_money(cls, df_by_sentence: DataFrame):
        try:
            money_words = ['money', 'finance', 'financial', 'financially']

            if any(i in df_by_sentence.word.values for i in money_words):
                prp = ['they', 'he', 'she']
                have = ['have']
                if Nlp_util.are_words1_words2_words3_in_order(df_by_sentence, prp, have, money_words):
                    return False
                else:
                    return True
            elif Nlp_util.are_words1_words2_words3_in_order(df_by_sentence, ['i'], ['poor']):
                return True
            else:
                return False
        except:
            logging.exception('')
            return False

    @classmethod
    def __is_about_missing(cls, df_by_sentence):
        try:
            phrase1 = ['i']
            phrase2 = ['miss']

            return Nlp_util.are_words1_words2_words3_in_order(df_by_sentence, phrase1, phrase2)
        except:
            logging.exception('')
            return False
