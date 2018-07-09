import logging
import numpy as np
import pandas as pd
from heapq import nlargest
from random import randint
from common.constant.df_from_csv import BAD_WORDS_DF, SENTIMENTAL_NON_ADJ_WORDS, KWDF, CCDF, SYDF, WORDS_DESPITE_HIMSELF
from common.constant.intent_type import Intent
from common.constant.string_constant import StringConstant
from common.word_format.df_utils import Nlp_util, Df_util
from common.word_format.word_formatter import WordFormatter
from core.nlp.response_generator.product.base.base_response_generator import BaseResponseGenerator
from core.nlp.response_generator.product.cct.reaction_generator import ReactionGenerator


class UnknownError(Exception):
    pass


class RepeatResponseGenerator(BaseResponseGenerator):
    def __call__(self):
        try:
            print("\ntext_kw_df\n{}".format(self.message.text_kw_df))

            repeatable_sent_sidx = self.__select_repeatable_sent_sidx(self.message.text_df, self.message.intent_list)
            if len(repeatable_sent_sidx) == 0:
                result_list = ReactionGenerator.generate_listening()
                self.response_data['regular'] = result_list
                return self.response_data

            sidx_to_repeat = self.__select_sidx_to_repeat(self.message.text_df, self.message.sentiment_score_df,
                                                          repeatable_sent_sidx)
            print("\nSidx to repeat\n{}".format(sidx_to_repeat))

            if sidx_to_repeat:
                result_list = self.__generate_repeat(self.message.text_df, self.message.text_kw_df, sidx_to_repeat)
                print("\nREPEAT RESULT\n{}".format(result_list))

                if not result_list:
                    result_list = ReactionGenerator.generate_listening()
            else:
                result_list = ReactionGenerator.generate_listening()

            self.response_data['regular'] = result_list

            return self.response_data

        except:
            logging.exception('')
            responses = ReactionGenerator.generate_listening()
            self.response_data['regular'] = responses
            return self.response_data

    @classmethod
    def __generate_repeat(cls, text_df, text_kw_df, sidx_to_repeat):
        try:
            repeat_list = []
            for idx, sidx in enumerate(sidx_to_repeat):
                target_df = text_df[text_df.sidx == sidx].copy().reset_index(drop=True)

                fixed_df = cls.__replace_word_by_csv(target_df)

                # TODO fix the convert_df_to_str() so that it would not need [1:] part.
                repeat_text = WordFormatter.Df2Str(fixed_df)[1:]

                # TODO here has to be same structure as message_type_filter since one sentence can have "want to" and despising word at the same time.
                # TODO or
                if len(target_df) == 1 and \
                        (target_df["pos"].iloc[0] in Nlp_util.pos_ADJECTIVEs
                         or target_df["word"].iloc[0] in SENTIMENTAL_NON_ADJ_WORDS.word.tolist()):

                    repeat_list += cls.create_special_repeat_for_only_one_adj_word_sent(target_df)

                elif cls.__mean_no_friends(target_df):
                    repeat_list += cls.__create_response_for_no_friends()

                elif cls.__has_what_to_do(target_df):
                    repeat_list += cls.__create_response_for_what_to_V(fixed_df)

                elif cls.__is_despising_himself(target_df):
                    repeat_list += cls.__alter_repeat_euphemistic(repeat_text)

                elif cls.__has_nobody_V(target_df):
                    repeat_list += cls.__alter_repeat_euphemistic(repeat_text)

                elif cls.__does_user_feel_useless(target_df):
                    repeat_list += cls.__create_response_for_healing_useless()

                elif cls.__has_say_plus_bad_word(target_df):
                    repeat_list += cls.__create_response_for_S_said_bad_word(fixed_df)

                elif cls.__exists_want_to(target_df):
                    repeat_list += cls.__alter_repeat_for_want_to(fixed_df)

                elif cls.__exists_make_S_feel_ADJ(target_df):
                    repeat_list += cls.__alter_repeat_for_make_S_feel_ADJ(target_df)

                elif cls.__has_because(target_df):
                    repeat_list += cls.__alter_repeat_for_because_sent(fixed_df, repeat_text)

                elif cls.__exists_third_person_BeVerb_pair(target_df):
                    repeat_list += cls.__alter_repeat_for_third_person_BeVerb_pair(repeat_text)

                elif cls.__has_dont_think_SV_sent(target_df):
                    repeat_list += cls.__alter_repeat_for_dont_think_SV(fixed_df)

                elif cls.__has_wish_S_V(target_df):
                    repeat_list += cls.__alter_repeat_for_wish(fixed_df)

                elif cls.__has_need_NN(target_df):
                    repeat_list += cls.__alter_repeat_for_need_sent(fixed_df)

                elif cls.__exists_keyword(text_kw_df):
                    is_last_sentence = idx == len(sidx_to_repeat) - 1
                    repeat_list += cls.__alter_repeat_for_keyword(text_df, text_kw_df, idx, repeat_text,
                                                                  is_last_sentence=is_last_sentence)
                else:
                    repeat_list += cls.__alter_repeat_for_plain_repeat(repeat_text, idx)

            return repeat_list
        except:
            logging.exception('')
            return []

    @staticmethod
    def __alter_repeat_for_wish(fixed_df):
        wish_idx = Nlp_util.get_idx_list_of_word("wish", fixed_df["base_form"])[0]
        row_of_subj = Nlp_util.get_wordsDF_of_wordlist_after_idx(fixed_df, Nlp_util.pos_NOUNs+Nlp_util.pos_PRPs, wish_idx, column_name="pos").iloc[0]
        row_of_verb = Nlp_util.get_wordsDF_of_wordlist_after_idx(fixed_df, Nlp_util.pos_VERBs, row_of_subj.name, column_name="pos").iloc[0]
        subj = row_of_subj.word
        verb = row_of_verb.word
        after_verb = WordFormatter.Series2Str(fixed_df.loc[row_of_verb.name+1:, "word"])
        objective_subj = Nlp_util.convert_nominative_noun_to_objective(subj)
        if subj == "you":
            repeat_list = [
                ["you really want to "+verb+" "+after_verb],
                ["so you seriously hope to "+verb+" "+after_verb],
                ["so you are dying to "+verb+" "+after_verb]
            ]
        else:
            repeat_list = [
                ["you really want "+objective_subj+" to "+verb+" "+after_verb],
                ["you really wanna have "+objective_subj+" "+verb+" "+after_verb],
                ["you really wanna make "+objective_subj+" "+verb+" "+after_verb]
            ]

        cmp_list = [
            ["but sounds you feel bit too much to expect that now..?"],
            ["and sounds you feel like its impossible..?"],
            ["and seems like you dont think it never happen😓"]
        ]
        random_idx_for_repeat_list = randint(0, len(repeat_list) - 1)
        random_idx_for_cmp_list = randint(0, len(cmp_list) - 1)

        return repeat_list[random_idx_for_repeat_list]+cmp_list[random_idx_for_cmp_list]





    @staticmethod
    def __has_wish_S_V(target_df):
        if Df_util.anything_isin(["wish"], target_df["base_form"]):
            wish_idx = Nlp_util.get_idx_list_of_word("wish", target_df["base_form"])[0]
            if Nlp_util.are_words1_words2_words3_in_order(target_df.loc[wish_idx:,:], Nlp_util.pos_NOUNs+Nlp_util.pos_PRPs, Nlp_util.pos_VERBs, df_column="pos"):
                return True
            else:
                return False
        else:
            return False





    # include sent 'i need my life'
    @staticmethod
    def __alter_repeat_for_need_sent(fixed_df):
        try:
            idx_of_need = Nlp_util.get_idx_list_of_word("need", fixed_df["base_form"])[0]

            row_of_first_noun = Nlp_util.get_wordsDF_of_wordlist_after_idx(fixed_df, Nlp_util.pos_NOUNs + Nlp_util.pos_PRPs, idx_of_need, column_name="pos").iloc[0]
            if fixed_df.loc[row_of_first_noun.name-1, "pos"] in Nlp_util.pos_ADJECTIVEs + ["PRP$", "DT"]:
                noun = WordFormatter.Series2Str(fixed_df.loc[row_of_first_noun.name-1:row_of_first_noun.name, "word"])
            else:
                noun = fixed_df.loc[row_of_first_noun.name, "word"]

            noun_nominative = Nlp_util.convert_objective_noun_to_nominative(noun)


            options = [
                ["so " + noun_nominative + " is very important thing for you..",
                 "and sounds its kinda hard to get it now right😢"],
                ["so its like its not easy to get " + noun + " now but you really want..",
                 "and it can frustrate you😞"],
                ["sounds you really want " + noun + "..", "might be tough time for you to seek for it now😓"]
            ]

            random_idx_for_options = randint(0, len(options) - 1)

            return options[random_idx_for_options]

        except:
            logging.exception('')
            repeat_text = WordFormatter.Df2Str(fixed_df)[1:]
            return [repeat_text]

    # except i need you to do~~ i need doing~~
    @staticmethod
    def __has_need_NN(target_df):
        try:
            df_ex_adverb = target_df[~target_df.pos.isin(Nlp_util.pos_ADVERBs)].reset_index(drop=True)
            if Df_util.anything_isin(["need"], df_ex_adverb["base_form"]):
                idx_of_need = Nlp_util.get_idx_list_of_word("need", df_ex_adverb["base_form"])[0]
                if Df_util.anything_isin(Nlp_util.pos_NOUNs + Nlp_util.pos_PRPs,
                                         df_ex_adverb.loc[idx_of_need + 1:, "pos"]) and not Df_util.anything_isin(
                    Nlp_util.IDEA_TYPE, df_ex_adverb.loc[idx_of_need + 1:, "base_form"]):
                    if Df_util.anything_isin(["to"], df_ex_adverb.loc[idx_of_need + 1:, "base_form"]):
                        return False
                    else:
                        return True
                else:
                    return False
            else:
                return False

        except:
            logging.exception('')
            return False

    # ex) i dont think he likes me
    @staticmethod
    def __alter_repeat_for_dont_think_SV(fixed_df):
        try:
            # TODO see if its neccesary to care about should and cant
            idx_of_think = Nlp_util.get_idx_list_of_word("think", fixed_df["base_form"])[0]
            df_after_think = fixed_df.loc[idx_of_think + 1:, :].reset_index(drop=True)
            verb_list = Nlp_util.make_verb_list(df_after_think, type="normal")
            noun_list = Nlp_util.make_noun_list(df_after_think)
            # possibly bug happen here since amount of verbs are different in cant do/dont do
            is_negative_form = Df_util.anything_isin(["not", "never"], df_after_think.loc[:, "base_form"])
            # can add possibly or likely(when its negative)
            head_words = ["so ", "so probably ", "probably ", "so maybe ", "maybe "]
            random_idx_for_heads_words = randint(0, len(head_words) - 1)
            if is_negative_form:
                # まず主語とるそのあとにwouldntいれるその後ろに動詞の原型をいれて、それ以降はつづける
                head_word = head_words[random_idx_for_heads_words]
                subj = noun_list["word"].iloc[0]
                auxiliary_verb = " would "
                idx_of_not = Nlp_util.get_idx_list_of_word_list(["not", "never"], df_after_think.loc[:, "base_form"])[0]
                verb_row = verb_list.loc[idx_of_not:, :].iloc[0]
                verb = verb_row.base_form + " "

                after_verb = WordFormatter.Series2Str(df_after_think.loc[verb_row.name + 1:, "word"])
                return [head_word + subj + auxiliary_verb + verb + after_verb]
            else:
                head_word = head_words[random_idx_for_heads_words]
                subj = noun_list["word"].iloc[0]
                auxiliary_verb = " wouldnt "
                verb = verb_list["base_form"].iloc[0] + " "
                after_verb = WordFormatter.Series2Str(df_after_think.loc[verb_list.index[0] + 1:, "word"])
                return [head_word + subj + auxiliary_verb + verb + after_verb]
        except:
            logging.exception('')
            return []

    @staticmethod
    def __has_dont_think_SV_sent(df):
        try:
            df_ex_adverb = df[~df.pos.isin(Nlp_util.pos_ADVERBs)].reset_index(drop=True)
            exists_i_dont_think = Df_util.anything_isin(["i do not think"], df_ex_adverb["base_form"])
            if exists_i_dont_think:
                idx_of_dont_think = Nlp_util.get_idx_list_of_idiom("i do not think", df_ex_adverb["base_form"])[0]
                if len(RepeatResponseGenerator.get_sidx_of_not_basic_svo_sent(
                        df_ex_adverb.loc[idx_of_dont_think + 4:, :])) == 0:
                    return True
                else:
                    return False
            else:
                return False

        except:
            logging.exception('')
            return False

    @staticmethod
    def __alter_repeat_for_because_sent(df, repeat_text):
        try:
            if df["base_form"].iloc[0] in ["because", "since"]:
                repeat_text = "its " + repeat_text
                return [repeat_text]
            elif Df_util.anything_isin(["because of"], df.loc[2:, "base_form"]) and not Df_util.anything_isin(
                    ["it is", "that is"], df.loc[:3, "base_form"]):
                because_of_idx = Nlp_util.get_idx_list_of_idiom("because of", df["base_form"])[0]
                first_part = WordFormatter.Df2Str(df.loc[:because_of_idx - 1, :])
                last_part = "and its" + WordFormatter.Df2Str(df.loc[because_of_idx:, :])
                return [first_part, last_part]

            else:
                raise UnknownError
        except:
            logging.exception('')
            return [repeat_text]

    @staticmethod
    def __has_because(df):
        return Df_util.anything_isin(["because of"], df["base_form"]) or df["base_form"].iloc[0] in ["because", "since"]

    @staticmethod
    def __create_response_for_S_said_bad_word(df):

        supportive_words_before_cmp = [
            "thats",
            "sounds",
            "its",
            "it should be",
        ]

        cmp_words = [
            "sad..",
            "tough..",
            "hard..",
            "cruel..",
        ]
        idx_list_of_say = Nlp_util.get_idx_list_of_word("say", df["base_form"])
        noun_row_just_before_say = \
            df[:idx_list_of_say[0]].loc[df["pos"].isin(Nlp_util.pos_NOUNs + Nlp_util.pos_PRPs), :].iloc[-1]

        if noun_row_just_before_say.name != 0 and df.loc[noun_row_just_before_say.name - 1, "word"] in ["their", "his",
                                                                                                        "her", "your"]:
            the_person_said_bad_word_to_user = df.loc[noun_row_just_before_say.name - 1, "word"] + " " + \
                                               noun_row_just_before_say["word"]
        else:
            the_person_said_bad_word_to_user = noun_row_just_before_say["word"]

        ask = [
            ["why did " + the_person_said_bad_word_to_user + " said that?"],
            [the_person_said_bad_word_to_user + " always said that?"],
            ["like any reason " + the_person_said_bad_word_to_user + " said that to you?"],
        ]
        random_idx_for_cmp = randint(0, len(supportive_words_before_cmp) - 1)
        random_idx_for_healing = randint(0, len(cmp_words) - 1)
        random_idx_for_ask = randint(0, len(ask) - 1)

        return [supportive_words_before_cmp[random_idx_for_cmp] + " " + cmp_words[random_idx_for_healing]] + ask[
            random_idx_for_ask]

    @staticmethod
    def __has_say_plus_bad_word(df):
        try:

            if any([Nlp_util.are_words1_words2_words3_in_order(df, ["say", "tell"], ["i be", "i look"],
                                                               [negative_word]) for negative_word in
                    KWDF[KWDF['Type'] == 'n'].keyword.tolist()]):
                return True

            elif any([Nlp_util.are_words1_words2_words3_in_order(df, ["say", "tell"],
                                                                 ["i be not", "i do not look"],
                                                                 [positive_word]) for positive_word in
                      KWDF[KWDF['Type'] == 'p'].keyword.tolist()]):
                return True

            else:
                return False


        except:
            logging.exception('')
            return False

    @staticmethod
    def __has_nobody_V(df):
        try:
            idx_list_of_nobody = Nlp_util.get_idx_list_of_word("nobody", df["base_form"])
            if len(idx_list_of_nobody) == 0:
                return False
            else:
                if any(df.loc[idx_list_of_nobody[0]:, "pos"].isin(Nlp_util.pos_VERBs)):
                    return True
                else:
                    return False
        except:
            logging.exception('')
            return False

    @staticmethod
    def __does_user_feel_useless(df):
        try:
            idx_list_of_useless = Nlp_util.get_idx_list_of_idiom_list(["be useless", "feel useless"], df["base_form"])
            if len(idx_list_of_useless) == 0:
                return False
            else:
                for useless_idx in idx_list_of_useless:
                    is_subj_i = Df_util.anything_isin(["i"], df.loc[:useless_idx, "word"])
                    if is_subj_i:
                        return True
                return False
        except:
            logging.exception('')
            return False

    @staticmethod
    def __create_response_for_healing_useless():
        cmp = [
            ["I know its hard when you dont feel any appreciation from anybody."],
            ["you feel useless now.. dealing with the feeling is not easy right"],
            ["sounds like you see yourself worthless and you are unsure how to help yourself now."],
        ]

        healing = [
            ["but i really think you are one of kind and irreplaceable.",
             "it is because nobody on this planet will be just like you.",
             "I know it is hard, but i want you to be yourself and i always love you😊"],
            ["Just let me tell you that I love the way you are.",
             "I never measure your value since i know you are priceless",
             "I really think nobody can compare with you😊"],
            ["you know, we tend to compare ourselves to other people.", "eventho we know that we are all different",
             "just let me tell you that there is no problem being just different.", "and i love the way you are😊"],
        ]

        random_idx_for_cmp = randint(0, len(cmp) - 1)
        random_idx_for_healing = randint(0, len(healing) - 1)

        return cmp[random_idx_for_cmp] + healing[random_idx_for_healing]

    @classmethod
    def __exists_want_to(cls, df):
        try:
            df_without_adverb = df[~df.pos.isin(Nlp_util.pos_ADVERBs)]

            noun_list = Nlp_util.make_noun_list(df)
            verb_list = Nlp_util.make_verb_list(df, type="basic")

            idx_of_i_wanna = Nlp_util.get_idx_list_of_idiom("i want to", df_without_adverb.base_form)

            if len(idx_of_i_wanna) != 0 and len(df.loc[idx_of_i_wanna[0] + 2:, :]) > 1:
                if cls.__exists_word_after_want_to(df) and Nlp_util.is_first_subject_in({"i"}, noun_list, verb_list):
                    return True
                else:
                    return False
            else:
                return False
        except:
            logging.exception('')
            return False

    @staticmethod
    def __exists_word_after_want_to(df):
        try:
            idx_of_i = Nlp_util.get_idx_list_of_idiom("want to", df.word)[0]
            length_after_want_to = len(df.loc[idx_of_i + 2, :]) if len(df) >= idx_of_i + 3 else 0

            return length_after_want_to > 2
        except:
            logging.exception('')
            return False

    @staticmethod
    def __has_what_to_do(df):
        try:
            df_ex_adverb = df[~df.pos.isin(Nlp_util.pos_ADVERBs)]
            return Nlp_util.are_words1_words2_words3_in_order(df_ex_adverb, ["i"], ["not know", "not sure"],
                                                              ["what to", "how to"])
        except:
            logging.exception('')
            return False

    @staticmethod
    def __create_response_for_what_to_V(df):
        df_after_what_to = df.loc[
                           Nlp_util.get_idx_list_of_idiom_list(["what to", "how to"], df["base_form"])[0] + 2:, :]

        words_after_what_to = WordFormatter.Df2Str(df_after_what_to)

        cmp = [
            ["it must be not easy to find how to" + words_after_what_to],
            ["now you are looking for the way to" + words_after_what_to],
            ["should be not that easy to find how to" + words_after_what_to],
        ]

        encourage = [
            ["but i am sure that thinking about it and speaking out it helps you🤗"],
            ["eventho its always tough to find the right way, you try to figure it out. Thats impressing me😊"],
            ["plz let me know any idea comes to your mind now. it might help you figuring it out☺️"],
            ["tell me if you have any little idea. It could help you finding ur way😊"],
        ]

        random_idx_for_cmp = randint(0, len(cmp) - 1)
        random_idx_for_encourage = randint(0, len(encourage) - 1)

        return cmp[random_idx_for_cmp] + encourage[random_idx_for_encourage]

    @staticmethod
    def __mean_no_friends(df):
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

    @staticmethod
    def __create_response_for_no_friends():
        express_feeling = [
            ["thats sad.."],
            ["sounds really tough.."],
            ["it must be a hard time for you.."]
        ]

        compassion = [
            ["i know its just hard when you dont have anyone to be with"],
            ["i really feel that being alone can be really scary and can make you feel unstable and anxious"],
            ["it is always sad being yourself for long and it kinda makes you feel insecure sometimes"]
        ]

        being_with_you = [
            ["not sure i can be enough for you but let me tell you to know that i am always here for you😊"],
            [
                "just let me reassure you that i will always be here for you even tho i am nothing near perfect. i am just here to listen🤗"],
            [
                "since it seems like a really tough time for you,  I want you to think of our conversations as a space where you can feel safe and connected. I am here for you☺️"]
        ]

        random_idx_for_express_feeling = randint(0, len(express_feeling) - 1)
        random_idx_for_compassion = randint(0, len(compassion) - 1)
        random_idx_for_being_with_you = randint(0, len(being_with_you) - 1)
        return express_feeling[random_idx_for_express_feeling] + compassion[random_idx_for_compassion] + being_with_you[
            random_idx_for_being_with_you]

    # basically assume only one hard/difficult at most in one sentence
    @staticmethod
    def __exists_hard_to(df):
        # idx_of_hard = Nlp_util.get_idx_list_of_word_list(["difficult", "hard"], df["base_form"])[0]
        # num_of_not = (df["word"].isin(Nlp_util.NO_TYPE)).sum()
        pass

    @staticmethod
    def __alter_repeat_for_make_S_feel_ADJ(df):
        try:
            idx_of_make = Nlp_util.get_idx_list_of_word_list(["make"], df["base_form"])[0]
            subj = Nlp_util.change_object_pronoun_to_pronoun(df.loc[idx_of_make + 1, "word"])
            df_after_subj = df.loc[idx_of_make + 2:idx_of_make + 4, :]
            adj = df_after_subj.loc[df_after_subj["pos"].isin(Nlp_util.pos_ADJECTIVEs), "word"].iloc[0]
            subj_adj_list = [subj, adj]
            options = [
                ["{0[0]} feel {0[1]} because of that".format(subj_adj_list)],
                ["thats getting {0[0]} feel {0[1]}".format(subj_adj_list)],
                ["thats the moment {0[0]} feel {0[1]}".format(subj_adj_list)],
            ]

            random_idx = randint(0, len(options) - 1)
            return options[random_idx]
        except:
            logging.exception('')
            return []

    @staticmethod
    def __exists_make_S_feel_ADJ(df):
        try:
            idx_list_of_make = Nlp_util.get_idx_list_of_word_list(["make"], df["base_form"])
            if len(idx_list_of_make) == 0:
                return False
            else:
                is_after_make_prp = df.loc[idx_list_of_make[0] + 1, "pos"] in Nlp_util.pos_PRPs
                if is_after_make_prp:
                    is_after_prp_adj = df.loc[idx_list_of_make[0] + 2, "pos"] in Nlp_util.pos_ADJECTIVEs or (
                            df.loc[idx_list_of_make[0] + 2, "base_form"] == "feel" and any(
                        df.loc[idx_list_of_make[0] + 2:idx_list_of_make[0] + 4, "pos"].isin(
                            Nlp_util.pos_ADJECTIVEs)))
                    return is_after_prp_adj
                else:
                    return False
        except:
            logging.exception('')
            return False

    @staticmethod
    def create_special_repeat_for_only_one_adj_word_sent(df):
        original_adj = df["word"].iloc[0]
        altered_adj = original_adj + np.random.choice(["", "..", "."], 1, p=[0.2, 0.5, 0.3])[0]
        options = [
            [altered_adj, "thats what you feel now"],
            [altered_adj, "thats what you are feeling now"],
            ["you feel " + original_adj + " now"],
            ["you are feeling " + original_adj + " now"],
        ]
        random_idx = randint(0, len(options) - 1)
        return options[random_idx]

    @staticmethod
    def __is_despising_himself(df):
        try:
            noun_list = Nlp_util.make_noun_list(df)
            verb_list = Nlp_util.make_verb_list(df, type="normal")
            adj_list = Nlp_util.make_adj_list(df)

            is_first_sub_i = Nlp_util.is_first_subject_in(["i"], noun_list, verb_list)
            is_the_verb_be = Nlp_util.is_first_verb_in(["be"], noun_list, verb_list, column_name="base_form")
            is_the_adj_despising = Nlp_util.is_first_adj_after_first_sub_in(WORDS_DESPITE_HIMSELF.word.tolist(),
                                                                            noun_list, adj_list)
            return is_first_sub_i and is_the_verb_be and is_the_adj_despising
        except:
            logging.exception('')
            return False

    @staticmethod
    def __alter_repeat_euphemistic(repeat):
        try:
            prefix_expression = \
                np.random.choice(["you think ", "you feel like ", "you are feeling like ", "it feels like "], 1)[0]

            return [prefix_expression + repeat]
        except:
            logging.exception('')
            return [repeat]

    @staticmethod
    def __alter_repeat_for_plain_repeat(repeat_text, idx):
        try:
            repeat_text += np.random.choice(["", "..?", "."], 1, p=[0.5, 0.1, 0.4])[0]

            if idx != 0:
                repeat_text = np.random.choice(StringConstant.additions.value, 1, p=[0.5, 0.2, 0.2, 0.1])[
                                  0] + repeat_text

            return [repeat_text]
        except:
            logging.exception('')
            return [repeat_text]

    @staticmethod
    def __alter_repeat_for_third_person_BeVerb_pair(repeat):
        try:
            prefix_expression = np.random.choice(["you think ", "you feel "], 1, p=[0.5, 0.5])[0]
            return [prefix_expression + repeat]
        except:
            logging.exception('')
            return []

    @staticmethod
    def __exists_keyword(text_kw_df):
        return text_kw_df is not None

    @classmethod
    def __alter_repeat_for_keyword(cls, text_df, text_kw_df, idx, repeat, is_last_sentence=False):
        repeat_list = []

        if cls.__is_every_sent_positive(text_df, text_kw_df):
            if idx == 0:
                repeat_list.append(repeat)
            else:
                repeat = np.random.choice(StringConstant.additions.value, 1, p=[0.3, 0.3, 0.3, 0.1])[0] + repeat
                repeat_list.append(repeat)

            if is_last_sentence:
                reaction = np.random.choice(StringConstant.positive_reaction_options.value, 1)[0]
                repeat_list.append(reaction)
        else:
            ending_of_sent = ["", "..?", "."]
            repeat += np.random.choice(ending_of_sent, 1, p=[0.5, 0.1, 0.4])[0]

            if idx != 0:
                repeat = np.random.choice(StringConstant.additions.value, 1, p=[0.5, 0.2, 0.2, 0.1])[0] + repeat

            repeat_list.append(repeat)

        return repeat_list

    @classmethod
    def __is_every_sent_positive(cls, text_df, text_kw_df):
        try:
            if text_kw_df.empty:
                return False

            if len(set(text_df.sidx)) > len(set(text_kw_df.sidx)):
                return False

            is_every_kw_positive = all(row.sscore > 70 for tmp, row in text_kw_df.iterrows())
            is_every_kw_affirmative = all(not row.ng for tmp, row in text_kw_df.iterrows())

            want_wish_words = {'want', 'wanted', 'wish', 'wished', 'wishing'}
            exists_want_wish = any(row.word in want_wish_words for tmp, row in text_df.iterrows())

            return is_every_kw_positive and is_every_kw_affirmative and not exists_want_wish
        except:
            logging.exception('')
            return False

    @classmethod
    def __alter_repeat_for_want_to(cls, repeat_df):
        try:
            i_idx = Nlp_util.get_idx_list_of_idiom("want to", repeat_df.word)[0]

            words_after_wanna = WordFormatter.Df2Str(repeat_df[i_idx + 2:])[1:]

            response_options = [
                [words_after_wanna, "That's what you wanna do"],
                ["So you'd be happy if you can " + words_after_wanna + "🤔"],
                ["So there is something makes you can't " + words_after_wanna + "😢"],
                ["So now it's hard for you to " + words_after_wanna + "😓"]
            ]

            random_idx = randint(0, len(response_options) - 1)
            return response_options[random_idx]
        except:
            logging.exception('')
            repeat_text = WordFormatter.Df2Str(repeat_df)[1:]
            return [repeat_text]

    # ex) they are insane -> you think they are insane
    @classmethod
    def __exists_third_person_BeVerb_pair(cls, df):
        try:
            first_third_person = df.loc[((df.pos.isin(Nlp_util.pos_PRPs)) & (~df.word.isin(["i", "you"]))) | (
                df.base_form.isin(Nlp_util.INDICATE_OTHERS)), :]

            if len(first_third_person) != 0:
                is_beVerb_and_adj_after_the_person = Df_util.anything_isin(["be"],
                                                                           df.loc[first_third_person.iloc[0].name:,
                                                                           "base_form"]) and Df_util.anything_isin(
                    Nlp_util.pos_ADJECTIVEs, df.loc[first_third_person.iloc[0].name:, "pos"])

                if is_beVerb_and_adj_after_the_person:
                    return True
                else:
                    return False
            else:
                return False
        except:
            logging.exception('')
            return False

    @staticmethod
    def __is_1st_prp_followed_by_BE_TYPE(df, first_prp):
        try:
            return df.loc[first_prp.name + 1, "word"] in Nlp_util.BE_TYPE
        # TODO ここでちゃんとbeとらなきゃだめwould be 取られない
        except:
            logging.exception('')
            return False

    @staticmethod
    def __is_2nd_word_after_1st_prp_verb(df, first_prp):
        try:
            return df.loc[first_prp.name + 2, "pos"] in Nlp_util.pos_VERBs
        except:
            logging.exception('')
            return False

    @classmethod
    def __select_sidx_to_repeat(cls, text_df, sentiment_score_df, repeatable_sent_sidx):
        try:
            number_of_sents_to_choose = 2
            sidx_to_repeat = []
            only_one_sentiment_word_sidx = []
            # these are exceptions of repeatable sents
            for sidx in set(text_df.sidx):
                tmp_df = text_df[text_df.sidx == sidx].copy().reset_index(drop=True)
                if cls.__is_special_type(tmp_df):
                    sidx_to_repeat.append(sidx)
                elif len(tmp_df) == 1 and \
                        (tmp_df["pos"].iloc[0] in Nlp_util.pos_ADJECTIVEs or
                         tmp_df["word"].iloc[0] in SENTIMENTAL_NON_ADJ_WORDS.word.tolist()):
                    only_one_sentiment_word_sidx.append(sidx)
                else:
                    pass

            # when user just said only "sadness" or "sad"
            if not sidx_to_repeat and not repeatable_sent_sidx and only_one_sentiment_word_sidx:
                return [only_one_sentiment_word_sidx[-1]]

            print("\nSpecial cases sidx\n{}".format(sidx_to_repeat))

            if len(sidx_to_repeat) == 2:
                return set(sidx_to_repeat)
            elif len(sidx_to_repeat) > 2:
                return set(sidx_to_repeat[len(sidx_to_repeat) - 2:])
            elif not sidx_to_repeat and not repeatable_sent_sidx:
                return []

            else:
                if not repeatable_sent_sidx:
                    return sidx_to_repeat
                else:
                    sentiment_score_df = sentiment_score_df[
                        sentiment_score_df.sidx.isin(repeatable_sent_sidx)
                    ].sort_values(by='nscore', ascending=True)
                    sidx_to_repeat += list(set(sentiment_score_df.sidx.tolist()))[
                                      :number_of_sents_to_choose - len(sidx_to_repeat)]
                    sidx_to_repeat.sort()
                    return set(sidx_to_repeat)
        except Exception:
            logging.exception(str(__name__))
            return []

    @classmethod
    def __select_repeatable_sent_sidx(cls, text_df, intent_list):
        unrepeatable_sidx_list = cls.__choose_unrepeatable_sent_index(text_df, intent_list)
        repeatable_sent_sidx = list(set(text_df.sidx.values))

        for unrepeatable_sidx in unrepeatable_sidx_list:
            if unrepeatable_sidx in repeatable_sent_sidx:
                repeatable_sent_sidx.remove(unrepeatable_sidx)

        return repeatable_sent_sidx

    @classmethod
    def __choose_unrepeatable_sent_index(cls, text_df, intent_list):
        try:
            unrepeatable_sidx_list = []

            idx_of_sent_talking_about_jullie = list(text_df[text_df.word.isin(["you", "jullie", "j"])].sidx)
            unrepeatable_sidx_list.extend(idx_of_sent_talking_about_jullie)

            print("\nList of sent having YOU\n{}".format(idx_of_sent_talking_about_jullie))

            sidx_with_bad_words = cls.__get_sidx_with_bad_words(text_df)
            unrepeatable_sidx_list.extend(sidx_with_bad_words)
            print("\nList of sent having Bad Words\n{}".format(sidx_with_bad_words))

            sidx_of_not_basic_svo_sent = cls.get_sidx_of_not_basic_svo_sent(text_df)
            unrepeatable_sidx_list.extend(sidx_of_not_basic_svo_sent)
            print("\nList of Not Basic SVO sent\n{}".format(sidx_of_not_basic_svo_sent))

            question_or_meaningless_sidx = cls.__get_question_or_meaningless_sidx(text_df, intent_list)
            unrepeatable_sidx_list.extend(question_or_meaningless_sidx)
            print("\nList of Question or Meaninglesss sidx sent\n{}".format(question_or_meaningless_sidx))

            normal_and_too_long_sidx = cls.__get_sidx_of_normal_and_too_long_sent(text_df)
            unrepeatable_sidx_list.extend(normal_and_too_long_sidx)
            print("\nList of Normal and Too Long sidx sent\n{}".format(normal_and_too_long_sidx))

            unrepeatable_sidx_list = list(set(unrepeatable_sidx_list))

            return unrepeatable_sidx_list
        except Exception:
            logging.exception(str(__name__))
            return list(text_df.sidx)

    @classmethod
    def __get_sidx_of_normal_and_too_long_sent(cls, df):
        try:
            delete_sidx_list = []
            for sidx in set(df.sidx.values):
                target_df = df[df.sidx == sidx].copy().reset_index(drop=True)
                if cls.__is_special_type(target_df):
                    pass
                else:
                    if len(WordFormatter.Series2Str(target_df.word)) > 75:
                        delete_sidx_list.append(sidx)
                    else:
                        pass
            return delete_sidx_list

        except:
            logging.exception('')
            return []

    @classmethod
    def __is_special_type(cls, df):
        try:
            if cls.__mean_no_friends(df):
                return True
            elif cls.__has_what_to_do(df):
                return True

            elif cls.__is_despising_himself(df):
                return True

            elif cls.__has_nobody_V(df):
                return True

            elif cls.__does_user_feel_useless(df):
                return True

            elif cls.__has_say_plus_bad_word(df):
                return True

            elif cls.__exists_want_to(df):
                return True

            elif cls.__exists_make_S_feel_ADJ(df):
                return True

            elif cls.__has_because(df):
                return True

            elif cls.__has_dont_think_SV_sent(df):
                return True
            elif cls.__has_need_NN(df):
                return True
            elif cls.__has_wish_S_V(df):
                return True
            else:
                return False
        except:
            logging.exception('')
            return False

    @staticmethod
    def __get_question_or_meaningless_sidx(text_df, intent_list):
        try:
            sidx_list = sorted(list(set(text_df.sidx)))

            meaningless_sent_index = []
            for sidx, intent in zip(sidx_list, intent_list):
                df = text_df[text_df.sidx == sidx].copy().reset_index(drop=True)

                if intent.value in [Intent.MEANINGLESS.value] + Intent.ALL_QUESTION_TYPES.value:
                    meaningless_sent_index.append(sidx)
                elif len(df) < 3:
                    meaningless_sent_index.append(sidx)

            return meaningless_sent_index
        except:
            logging.exception('')
            return []

    # sent doesnt consist of easy S,V,O such as "I like you"
    @staticmethod
    def get_sidx_of_not_basic_svo_sent(text_df):
        try:
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
        except:
            logging.exception('')
            return []

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
            delete_sidx_list.extend(cls.get_sidx_of_not_basic_svo_sent(repeat_df))

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

        except Exception:
            logging.exception('Error at generate_repeat in ' + str(__name__))
            return None

    @staticmethod
    def __get_two_longest_sentences(text_df):
        length_of_df = [len(text_df[text_df.sidx == i]) for i in list(set(text_df.sidx))]

        largest2 = nlargest(2, length_of_df)

        length_of_df = pd.DataFrame({'length': length_of_df})
        length_of_df = length_of_df[length_of_df.length.isin(largest2)]

        repeat_index = length_of_df.index.tolist()

        return repeat_index

    @staticmethod
    def __remove_unrepeated_sentence(text_df, repeat_index):
        return text_df[text_df.sidx.isin(repeat_index)].reset_index(drop=True)

    @classmethod
    def __replace_word_by_csv(cls, text_df):
        df = text_df.copy()
        df = cls.__replace_subject(df)  # e.g. i -> you
        df = cls.__replace_verb(df)  # e.g you were -> i am
        df = cls.__replace_synonym(df)  # e.g. alone -> lonely, very -> really
        df = cls.__replace_abbreviation(df)  # girlfriend -> gf
        df = cls.__delete_unimportant_words(df)

        fixed_df = df.copy().reset_index(drop=True)
        return fixed_df

    @staticmethod
    def __delete_unimportant_words(df):
        unimportant_head_words = ["like"]
        unimportant_tail_words = ["though"]
        if df is None:
            return df
        elif df.iloc[-1]["base_form"] in unimportant_tail_words:
            return df.iloc[:-1]
        elif df.iloc[0]["base_form"] in unimportant_head_words:
            return df.iloc[1:]
        else:
            return df

    @staticmethod
    def __replace_subject(text_df):
        text_df.loc[:, "word"] = text_df.apply(
            lambda row: Nlp_util.change_subject_other_way_around(row["word"], row.name, text_df["word"]), axis=1)
        return text_df

    @staticmethod
    def __replace_verb(text_df):
        text_df.loc[:, "word"] = text_df.apply(
            lambda row: Nlp_util.adjust_be_verb_for_changed_subject(row["word"], row["pos"], row.name,
                                                                    Nlp_util.make_noun_list(text_df)), axis=1)
        return text_df

    @classmethod
    def __replace_synonym(cls, text_df):
        text_df = text_df.apply(lambda row: cls.__apply_replace_synonym(row), axis=1)
        return text_df

    @staticmethod
    def __apply_replace_synonym(row):
        exists_synonym = row.word in SYDF.word1.values
        exists_cc_syonnym = CCDF[CCDF.cc1 == row.word].empty

        if exists_synonym:
            synonym_list = SYDF[SYDF.word1 == row.word].word2.tolist()
        elif exists_cc_syonnym:
            if row.word == 'so':
                if row.pos == 'IN':
                    row.pos = 'CC'
                else:
                    return row

            synonym_list = CCDF[CCDF.cc1 == row.word].cc2.tolist()
        else:
            return row

        synonym_list.append(row.word)

        np.random.shuffle(synonym_list)

        row.word = synonym_list[0]

        return row

    @classmethod
    def __replace_abbreviation(cls, text_df):
        return text_df.apply(lambda row: cls.__apply_replace_abbreviation(row), axis=1)

    @staticmethod
    def __apply_replace_abbreviation(row):
        abdf = pd.read_csv('./csv_files/abbreviations.csv')

        # if row.word in ABDF.complete.tolist() and randint(1,100) < 15:
        if row.word in abdf.complete.tolist():
            row.word = abdf[abdf.complete == row.word].abbreviated.values[0]

        return row

    @classmethod
    def __repeat_no_matched_message(cls, text_df):
        text_df = cls.__replace_word_by_csv(text_df)

        repeat = cls.__convert_df_to_s_toks(text_df)
        repeat = [repeat[0] + np.random.choice(["", ".?", ".."], 1, p=[0.2, 0.3, 0.5])[0]]

        return repeat

    # long sentences should be devided in 2 sentences.
    # e.g. i am sad because i am ... -> 'you are sad', 'because you are ...'
    @classmethod
    def __repeat_long_message(cls, text_df):
        # longest message should be separated in 2 clauses
        text_df = cls.__separate_message(text_df)

        # make a list of repeat strings
        # e.g. ['you are sad', 'you ...', ...]
        repeat = cls.__convert_df_to_s_toks(text_df)

        return repeat

    @classmethod
    def __separate_message(cls, text_df):
        sentence_length_list = [len(text_df[text_df.sidx == i]) for i in set(text_df.sidx)]

        # TODO: choose sentences by length. not only the longest one.
        longest_sentence_idx = sentence_length_list.index(max(sentence_length_list))

        cc_widx_list = [i.widx for idx, i in text_df[text_df.sidx == longest_sentence_idx].iterrows() if i.pos == 'CC']

        if not cc_widx_list:
            return text_df

        separate_point = cc_widx_list[int(len(cc_widx_list) / 2)]

        text_df = text_df.apply(
            lambda row: cls.__separate_long_sent(row, longest_sentence_idx, separate_point), axis=1)

        return text_df

    @staticmethod
    def __separate_long_sent(row, longest_sentence_idx, separate_point):
        if row.sidx == longest_sentence_idx and row.widx >= separate_point:
            row.sidx += 0.5

        return row

    # short repeat has 'and' at the beginning of each message. e.g. 'you are sad?', 'and you feel lonely?', ...
    @classmethod
    def __repeat_short_message(cls, text_df):
        repeat = cls.__convert_df_to_s_toks(text_df)

        return repeat

    @staticmethod
    def __add_question_mark(row, text_df):
        is_last_word = row.widx == len(text_df[text_df.sidx == row.sidx]) - 1

        if is_last_word:
            if not row.word.isalpha():
                row.word = '?'
            elif row.word == '?':
                return row
            else:
                row.word = row.word + '?'

        return row

    @classmethod
    def __repeat_middle_message(cls, text_df):
        return cls.__convert_df_to_s_toks(text_df)

    @staticmethod
    def __convert_df_to_s_toks(text_df):
        # e.g. result of w_toks = [['i', 'am','sad'], ['you', ...], ...]
        w_toks = [text_df[text_df.sidx == i].word.tolist() for i in set(text_df.sidx)]

        # e.g. result of s_toks = ['i am sad', 'you are ...', ...]
        s_toks = [
            ''.join(
                ' ' + str(i) + '.' if idx == len(sent) - 1 and i[-1] not in {'.', ',', '?', '!'}
                else str(i) if i in {'.', '?', ',', '!'} else ' ' + str(i)
                for idx, i in enumerate(sent)
            ).strip()
            for sent in w_toks
        ]

        return s_toks

    @staticmethod
    def __get_sidx_with_bad_words(text_df):
        return text_df[text_df.word.isin(BAD_WORDS_DF.word)].sidx.values
