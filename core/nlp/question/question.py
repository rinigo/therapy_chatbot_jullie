import pandas as pd
import random
import logging
from common.word_format.df_utils import Df_util
from common.word_format.df_utils import Nlp_util
from core.nlp.df_generator import original_df_generator
import numpy as np
from core.nlp.pos_tagger import PosTagger

pd.options.mode.chained_assignment = None



class NoSubjectError(Exception):
    pass


class NoVerbError(Exception):
    pass


class UnknownError(Exception):
    pass



class DetectQuestion:
    be_do_md = ["was", "wastnt", "wasn't", "are", "aren't", "arent", "isnt", "is", "isn't", "do", "don't", "dont",
                      "did", "didnt", "didn't", "can", "cant", "can't", "could","am",
                      "couldn't", "couldnt",
                      "may", "might", "would", "wouldnt", "wouldn't", "should", "shouldnt", "shouldn't", "have", "had",
                      "havent"]
    what_how = ["how", "what", "why", "who", "which", "when"]

    all_question_words = be_do_md+what_how

    def __init__(self, df):
        self.df = df
        self.noun_list = Nlp_util.make_noun_list(self.df)
        self.verb_list = Nlp_util.make_verb_list(self.df)

    @staticmethod
    def is_question_form(df, noun_list, verb_list):
        # clouse_label = {"S","SBAR","SBARQ","SINV","SQ"}
        try:
            df_ex_adverb = df[~df.pos.isin(Nlp_util.pos_ADVERBs)].reset_index(drop=True)
            if df_ex_adverb.empty:
                return False
            elif Nlp_util.is_last_word(["?"], df_ex_adverb):
                return True

            # cases like "do you"
            elif Nlp_util.is_first_word_in(DetectQuestion.all_question_words, df_ex_adverb) and len(verb_list) == 0 and len(noun_list) == 0:
                return True

            elif len(verb_list) == 0:
                return False

            elif Nlp_util.is_first_word_in(DetectQuestion.what_how, df_ex_adverb) and (Nlp_util.is_second_words_pos_in(["MD"], df_ex_adverb) or Nlp_util.is_second_word_in(["be"], df_ex_adverb, column_name="base_form")):
                return True

            elif Nlp_util.is_first_word_in(DetectQuestion.be_do_md, df_ex_adverb) and Nlp_util.is_second_words_pos_in(Nlp_util.pos_NOUNs + Nlp_util.pos_PRPs, df_ex_adverb):
                return True

            elif len(noun_list) == 0:
                return False

            else:
                return False

        except Exception:
            logging.exception("Error at is_question_form: ")
            return False


# class to run question processing
class Test:
    def __init__(self, tokenized_sent):
        # self.df = WillBeSent_df(text)
        tmp = DetectQuestion(tokenized_sent)
        if DetectQuestion.is_question_form(tmp.df, tmp.noun_list, tmp.verb_list):
            print("this is a question!")
            self.text = tokenized_sent
            self.result = DefineQuestionType(tokenized_sent).categorize_by_leading_word()
        else:
            print("this is not a question!")


# QuestionTypeClassを返す
class DefineQuestionType:
    q_type = ""

    def __init__(self, df):
        # w_toks = MessageNormalizer.normalize_message_for_question(question_w_tok)
        # self.original_df = original_df_generator.OriginalDFGenerator.create_original_df_by_w_toks([question_w_tok])
        self.df = self.fix_df(df)
        self.noun_list = Nlp_util.make_noun_list(self.df)
        self.verb_list = Nlp_util.make_verb_list(self.df)

    def fix_df(self, df):
        try:
            df = Nlp_util.joint_have_to(df)
            df = Nlp_util.cut_unnecessary_words(df)
            df = Nlp_util.joint_continuous_words_by_pos(["VBG"], ["JJ"], "NN", df)
            # DT + PRPの場合は結合しない。ex) do you know that she hates me?
            df = Nlp_util.joint_continuous_words_by_pos(["DT"], ["NN"], ["NN"], df, Nlp_util.IDEA_TYPE + Nlp_util.SP_TYPE1)
            df = Nlp_util.change_subject_dt_to_nn(df)
            return df
        except:
            logging.exception('')
            return df



    def is_inbetween_2nd_sub_and_verb(self, word_list, second_subject_idx, verb_idx_of_second_subject):
        return Df_util.anything_isin(word_list, self.df.loc[second_subject_idx:verb_idx_of_second_subject, "word"])

    def is_any_noun_after(self, word_list):
        return any(self.noun_list.index > self.df.loc[self.df["word"].isin(word_list), "word"].index[0])

    def make_second_subject_idx(self):
        return self.noun_list.index[1]

    def make_verb_idx_of_second_subject(self, second_subject_idx):
        return self.verb_list[self.verb_list.index > second_subject_idx].index[0]

    def judge_sent_hasnt_verb_subject(self):
        if Df_util.nothing_isin(["for"], self.df["word"]) or Df_util.nothing_isin(["what", "who"], self.df["word"]):
            raise NoVerbError
        else:
            for_idx_list = Nlp_util.make_idx_list_by(["for"], self.df)
            what_idx_list = Nlp_util.make_idx_list_by(["what", "who"], self.df)
            for_what_idx_list = Df_util.make_pair_words_idx_list(for_idx_list, what_idx_list)
            if len(for_what_idx_list) == 0:
                return NoVerbError
            else:
                return ForWhatQuestionType(self, "special")

    def judge_double_subjects_general(self):
        second_subject_idx = self.make_second_subject_idx()
        verb_idx_of_second_subject = self.make_verb_idx_of_second_subject(second_subject_idx)

        if Nlp_util.is_second_subject_in({"you"}, self.noun_list):
            if self.is_inbetween_2nd_sub_and_verb(["would"], second_subject_idx, verb_idx_of_second_subject):
                return WouldQuestionType(self, "think_with_several_subject")
            else:
                return DoQuestionType(self, "think_with_several_subject")
        else:
            if self.is_inbetween_2nd_sub_and_verb(Nlp_util.SHOULD_TYPE, second_subject_idx, verb_idx_of_second_subject):
                return ShouldQuestionType(self, "think_with_several_subject", "better")
            elif self.is_inbetween_2nd_sub_and_verb(Nlp_util.CAN_TYPE, second_subject_idx, verb_idx_of_second_subject):
                return CanQuestionType(self, "think_with_several_subject", "can")
            else:
                return DoQuestionType(self, "think_with_several_subject")

    def judge_double_subjects_what(self):
        second_subject_idx = self.make_second_subject_idx()
        verb_idx_of_second_subject = self.make_verb_idx_of_second_subject(second_subject_idx)
        if self.is_inbetween_2nd_sub_and_verb(Nlp_util.SHOULD_TYPE, second_subject_idx, verb_idx_of_second_subject):
            return WhatQuestionType(self, "think_with_several_subject", "better")

        elif self.is_inbetween_2nd_sub_and_verb(Nlp_util.CAN_TYPE, second_subject_idx, verb_idx_of_second_subject):
            return WhatQuestionType(self, "think_with_several_subject", "can")

        else:
            return WhatQuestionType(self, "basic")

    def judge_double_subjects_how(self):
        second_subject_idx = self.make_second_subject_idx()
        verb_idx_of_second_subject = self.make_verb_idx_of_second_subject(second_subject_idx)
        if self.is_inbetween_2nd_sub_and_verb(Nlp_util.SHOULD_TYPE, second_subject_idx, verb_idx_of_second_subject):
            return HowQuestionType(self, "think_with_several_subject", "better")

        elif self.is_inbetween_2nd_sub_and_verb(Nlp_util.CAN_TYPE, second_subject_idx, verb_idx_of_second_subject):
            return HowQuestionType(self, "think_with_several_subject", "can")

        else:
            return HowQuestionType(self, "basic")

    def judge_single_or_double_subject_what_type(self, structure_type, auxiliary_verb=""):
        if Nlp_util.has_double_subjects(self.noun_list, self.verb_list):
            return self.judge_double_subjects_what()
        elif structure_type == "basic":
            return NoIdeaQuestionType(self, structure_type)
        else:
            return WhatQuestionType(self, structure_type)

    def judge_single_or_double_subject_how_type(self, structure_type, auxiliary_verb=""):
        if Nlp_util.has_double_subjects(self.noun_list, self.verb_list):
            return self.judge_double_subjects_how()
        else:
            return HowQuestionType(self, structure_type)

    def judge_what_do_sent(self):
        if len(self.verb_list) == 0:
            return NoVerbError
        elif Nlp_util.is_before_first_verb(["you"], self.df["word"], self.verb_list):
            if Nlp_util.is_first_verb_in(Nlp_util.THINK_TYPE, self.noun_list, self.verb_list):
                return self.judge_single_or_double_subject_what_type("basic")
            else:
                return WhatQuestionType(self, "basic")
        elif Nlp_util.is_before_first_verb(["i"], self.df["word"], self.verb_list):
            return NoIdeaQuestionType(self, "basic")
        elif Nlp_util.is_before_first_verb(["that", "it"], self.df["word"], self.verb_list):
            if Df_util.anything_isin(["mean"], self.df.loc[2:, "word"]):
                return GeneralQuestionType("RE", self)
            else:
                return WhatQuestionType(self, "basic")
        else:
            return WhatQuestionType(self, "basic")

    def judge_what_would_sent(self):
        if Nlp_util.is_any_verb_before_first_noun(self.noun_list, self.verb_list):
            if Nlp_util.is_before_first_noun(["progressive_form"], self.df["word"], self.noun_list):
                if Df_util.anything_isin(Nlp_util.SP_TYPE1, self.df["word"]):
                    return WhatQuestionType(self, "basic", "would")
                else:
                    return WhatQuestionType(self, "what_as_subject", "would")
            else:
                return WhatQuestionType(self, "what_as_subject", "would")
        elif len(self.noun_list) > 0:
            if Nlp_util.is_first_verb_in({"like"}, self.noun_list, self.verb_list):
                if Nlp_util.is_before_first_verb(["you"], self.df["word"], self.verb_list):
                    return GeneralQuestionType("JJ", self, "like")
                else:
                    return WhatQuestionType(self, "basic")
            elif Nlp_util.is_first_verb_in(Nlp_util.THINK_TYPE, self.noun_list, self.verb_list):
                return self.judge_single_or_double_subject_what_type("basic", "would")
            else:
                return WhatQuestionType(self, "basic")
        else:
            return WhatQuestionType(self, "what_as_subject", "would")

    def judge_what_be_sent(self):
        if Nlp_util.is_before_first_noun(Nlp_util.SP_TYPE1, self.df["word"], self.noun_list):
            return WhatQuestionType(self, "basic")
        elif Nlp_util.is_before_first_noun(["you"], self.df["word"], self.noun_list):
            if Nlp_util.is_first_verb_in({"thinking", "feeling", "considering"}, self.noun_list, self.verb_list):
                return self.judge_single_or_double_subject_what_type("progressive_form")
            else:
                return GeneralQuestionType("JJ", self, "be")
        elif Nlp_util.is_before_first_noun(["i"], self.df["word"], self.noun_list):
            return NoIdeaQuestionType(self, "basic")
        elif len(self.verb_list) > 1 and self.verb_list.iloc[1]["pos"] in {"VBG"}:
            return WhatQuestionType(self, "progressive_form")
        else:
            return WhatQuestionType(self, "what_as_subject")

    def judge_how_do_sent(self):
        if len(self.verb_list) == 0:
            raise NoVerbError
        elif Nlp_util.is_before_first_verb(["you"], self.df["word"], self.verb_list):
            if Nlp_util.is_first_verb_in(Nlp_util.THINK_TYPE, self.noun_list, self.verb_list):
                return self.judge_single_or_double_subject_how_type("basic")
            else:
                return HowQuestionType(self, "basic")
        elif Nlp_util.is_before_first_verb(["i"], self.df["word"], self.verb_list):
            # i_idx = self.df[self.df["word"]=="i"].index[0]
            if Nlp_util.is_first_verb_in({"know", "assure", "feel"}, self.noun_list, self.verb_list):
                if Nlp_util.is_after_first_verb_in({"you", "safe", "secure"}, self.df["word"], self.verb_list.index[0]):
                    return GeneralQuestionType("JJ", self, "safe")
                else:
                    return HowQuestionType(self, "basic")
            else:
                return HowQuestionType(self, "basic")


        elif Nlp_util.is_before_first_verb(["this"], self.df["word"], self.verb_list):
            # how does this workはJullieのシステムへの質問
            if Nlp_util.is_first_verb_in({"work"}, self.noun_list, self.verb_list):
                return GeneralQuestionType("JJ", self, "system")
            else:
                return HowQuestionType(self, "basic")
        else:
            return HowQuestionType(self, "basic")

    def judge_how_would_sent(self):
        if Nlp_util.is_any_verb_before_first_noun(self.noun_list, self.verb_list):
            if Nlp_util.is_before_first_noun(["progressive_form"], self.df["word"], self.noun_list):
                if Df_util.anything_isin(Nlp_util.SP_TYPE1, self.df["word"]):
                    return HowQuestionType(self, "basic")
                else:
                    return HowQuestionType(self, "how_as_subject")
            else:
                return HowQuestionType(self, "how_as_subject")
        elif Nlp_util.is_before_first_verb(["you"], self.df["word"], self.verb_list):
            if Nlp_util.is_first_verb_in({"like"}, self.noun_list, self.verb_list):
                return GeneralQuestionType("JJ", self, "like")

            elif Nlp_util.is_first_verb_in(Nlp_util.THINK_TYPE, self.noun_list, self.verb_list):
                return self.judge_single_or_double_subject_how_type("basic", "would")
            else:
                return HowQuestionType(self, "basic", "would")
        else:
            return HowQuestionType(self, "how_as_subject", "would")

    def judge_how_be_sent(self):
        if Nlp_util.is_before_first_noun(Nlp_util.SP_TYPE1, self.df["word"], self.noun_list):
            return HowQuestionType(self, "basic")
        elif Nlp_util.is_before_first_noun(["you"], self.df["word"], self.noun_list):
            if Nlp_util.is_first_verb_in({"thinking", "feeling", "considering"}, self.noun_list, self.verb_list):
                return self.judge_single_or_double_subject_how_type("progressive_form")
            else:
                return GeneralQuestionType("JJ", self, "be")
        elif Nlp_util.is_before_first_noun(["i"], self.df["word"], self.noun_list):
            return HowQuestionType(self, "basic")
        elif len(self.verb_list) > 1 and self.verb_list.iloc[1]["pos"] in {"VBG"}:
            return HowQuestionType(self, "progressive_form")
        else:
            return HowQuestionType(self, "be_adjective")

    def judge_sent_start_with_do(self):
        if len(self.verb_list) == 0:

            if len(self.noun_list) > 0:
                return GeneralQuestionType("RE", self)
            else:
                raise NoSubjectError
        elif Nlp_util.is_second_word_in({"u", "you"}, self.df):
            if Nlp_util.is_first_verb_in(Nlp_util.THINK_TYPE, self.noun_list, self.verb_list):
                if Nlp_util.has_double_subjects(self.noun_list, self.verb_list):
                    return self.judge_double_subjects_general()
                else:
                    return DoQuestionType(self, "basic")

            elif Nlp_util.is_first_verb_in({"agree"}, self.noun_list, self.verb_list):
                return AgreeQuestionType()

            elif Nlp_util.is_first_verb_in({"have"}, self.noun_list, self.verb_list):
                if Df_util.anything_isin(Nlp_util.IDEA_TYPE, self.df["word"]):
                    return NoIdeaQuestionType(self, "special")
                else:
                    return GeneralQuestionType("JJ", self)

            elif Nlp_util.is_first_verb_in(Nlp_util.SP_TYPE2, self.noun_list, self.verb_list):
                return GeneralQuestionType("JJ", self, "like")
            else:
                return GeneralQuestionType("JJ", self)

        elif Nlp_util.is_second_word_in({"i"}, self.df):
            if Df_util.nothing_isin(Nlp_util.pos_VERBs, self.df["pos"]):
                return DoQuestionType(self, "think_with_several_subject")
            elif Df_util.anything_isin(Nlp_util.SHOULD_TYPE, self.df["word"]):
                # return "ADCLS"
                return ShouldQuestionType(self, "basic", "better")
            else:
                return DoQuestionType(self, "basic")
        else:
            if Df_util.nothing_isin(Nlp_util.pos_VERBs, self.df["pos"]):
                raise NoVerbError
            elif Df_util.anything_isin(Nlp_util.SHOULD_TYPE, self.df["word"]):
                return ShouldQuestionType(self, "basic", "better")
            elif Df_util.anything_isin(Nlp_util.CAN_TYPE, self.df["word"]):
                return DoQuestionType(self, "basic", "can")
            else:
                return DoQuestionType(self, "basic")

    def judge_sent_start_with_can(self):
        if Nlp_util.is_second_word_in({"you"}, self.df):
            if Nlp_util.is_first_verb_in({"help", "talk", "tell", "check"}, self.noun_list, self.verb_list):
                return GeneralQuestionType("OR", self)
            else:
                return GeneralQuestionType("JJ", self)
        elif Nlp_util.is_second_word_in({"i"}, self.df):
            if len(self.noun_list) == 0:
                return GeneralQuestionType("OR", self)
            elif Nlp_util.is_first_verb_in({"tell", "talk", "ask"}, self.noun_list, self.verb_list):
                if Nlp_util.is_second_subject_in({"you"}, self.noun_list):
                    if Nlp_util.is_first_verb_in({"ask"}, self.noun_list, self.verb_list):
                        return GeneralQuestionType("OR", self)
                elif not Nlp_util.is_prp_in(
                        self.df.loc[Nlp_util.get_first_verb(self.noun_list, self.verb_list).name:, "pos"]):
                    return GeneralQuestionType("OR", self)
                else:
                    return CanQuestionType(self, "basic", "can")
            else:
                return CanQuestionType(self, "basic", "can")

        elif Nlp_util.is_second_word_in({"we"}, self.df):
            return GeneralQuestionType("OR", self)

        else:
            return CanQuestionType(self, "basic", "can")

    def judge_sent_start_with_be(self):
        if Nlp_util.is_second_word_in({"you"}, self.df):
            if len(self.verb_list) == 0:
                raise NoVerbError
            elif Df_util.anything_isin(["kidding", "serious", "crazy", "insane"], self.df.loc[2:, "word"]):
                return GeneralQuestionType("RE", self)
            elif Nlp_util.is_first_verb_in({"thinking", "feeling", "considering"}, self.noun_list, self.verb_list):
                return self.judge_double_subjects_general()
            elif Df_util.anything_isin(["robot", "human", "ai", "machine", "human being", "bot", "person"], self.df.loc[2:, "word"]):
                return GeneralQuestionType("Robot", self)
            else:
                return GeneralQuestionType("JJ", self, "be")
        elif Nlp_util.is_second_word_in({"i"}, self.df):
            if Df_util.anything_isin(["welcome"], self.df.loc[2:, "word"]):
                return GeneralQuestionType("JJ", self)

            elif len(self.verb_list) > 1 and self.verb_list.iloc[1]["pos"] in {"VBG"}:
                return DoQuestionType(self, "progressive_form")
            else:
                return BeQuestionType(self, "be_adjective")

        elif Nlp_util.is_second_word_in({"this", "here"}, self.df):
            if Df_util.anything_isin(["safe", "annonymous", "confidential", "private"], self.df.loc[1:, "word"]):
                return GeneralQuestionType("JJ", self, "safe")
            elif Df_util.anything_isin(["robot", "human", "ai", "machine", "human being", "bot", "person"], self.df.loc[2:, "word"]):
                return GeneralQuestionType("Robot", self)
            else:
                if len(self.verb_list) > 1:
                    if self.verb_list.iloc[1]["pos"] in {"VBG"}:
                        return DoQuestionType(self, "progressive_form")
                    else:
                        return BeQuestionType(self, "be_adjective")
                else:
                    return BeQuestionType(self, "be_adjective")
        else:
            if len(self.verb_list) > 1:
                if self.verb_list.iloc[1]["pos"] in {"VBG"}:
                    return DoQuestionType(self, "progressive_form")
                else:
                    return BeQuestionType(self, "be_adjective")
            else:
                return BeQuestionType(self, "be_adjective")

    def judge_sent_start_with_what(self):
        if len(self.noun_list) == 0:
            if any(self.df["pos"].isin(["DT"])):
                self.noun_list = self.df[self.df["pos"].isin(["DT"])]
            # この場合whatが主語となる
            elif Nlp_util.is_before_first_verb(Nlp_util.CAN_TYPE, self.df["word"], self.verb_list):
                return WhatQuestionType(self, "what_as_subject", "can")
            elif Nlp_util.is_before_first_verb(["should"], self.df["word"], self.verb_list):
                return WhatQuestionType(self, "what_as_subject", "should")
            elif Nlp_util.is_before_first_verb(["would"], self.df["word"], self.verb_list):
                return WhatQuestionType(self, "what_as_subject", "would")
            elif Nlp_util.is_before_first_verb(Nlp_util.BE_TYPE, self.df["word"], self.verb_list):
                return WhatQuestionType(self, "what_as_subject")
            else:
                raise NoSubjectError
        elif Nlp_util.is_before_first_noun(["if"], self.df["word"], self.noun_list):
            return WhatIfQuestionType(self, "special")
        elif Nlp_util.is_before_first_noun(["about"], self.df["word"], self.noun_list):
            return WhatAboutQuestionType(self, "special")
        elif Df_util.nothing_isin(Nlp_util.pos_VERBs, self.df["pos"]):
            raise NoVerbError

        elif Nlp_util.is_before_first_noun(Nlp_util.DO_TYPE, self.df["word"], self.noun_list):
            return self.judge_what_do_sent()
        elif Nlp_util.is_before_first_noun(Nlp_util.CAN_TYPE, self.df["word"], self.noun_list):
            if len(self.verb_list) == 0:
                raise NoVerbError
            elif self.is_any_noun_after(["can"]):
                return WhatQuestionType(self, "basic", "can")
            else:
                return WhatQuestionType(self, "what_as_subject", "can")
        elif Nlp_util.is_before_first_noun(["should"], self.df["word"], self.noun_list):
            if len(self.verb_list) == 0:
                raise NoVerbError
            elif self.is_any_noun_after(["should"]):
                return WhatQuestionType(self, "basic", "should")
            else:
                return WhatQuestionType(self, "what_as_subject", "should")
        elif Nlp_util.is_before_first_noun(["would"], self.df["word"], self.noun_list):
            return self.judge_what_would_sent()
        elif Nlp_util.is_before_first_noun(Nlp_util.BE_TYPE, self.df["word"], self.noun_list):
            return self.judge_what_be_sent()
        else:
            raise UnknownError

    def judge_sent_start_with_how(self):
        if Nlp_util.is_before_first_noun(["about"], self.df["word"], self.noun_list):
            return WhatAboutQuestionType(self, "think_with_several_subject")
        elif Df_util.nothing_isin(Nlp_util.pos_VERBs, self.df["pos"]):
            raise NoVerbError
        elif len(self.noun_list) == 0:
            # この場合whatが主語となる
            if Nlp_util.is_before_first_verb(["can", "could", "should", "would", "is", "was"], self.df["word"],
                                             self.verb_list):
                return HowQuestionType(self, "how_as_subject")
            else:
                raise NoSubjectError
        elif Nlp_util.is_before_first_noun(Nlp_util.DO_TYPE, self.df["word"], self.noun_list):
            return self.judge_how_do_sent()
        elif Nlp_util.is_before_first_noun(Nlp_util.CAN_TYPE, self.df["word"], self.noun_list):
            if len(self.verb_list) == 0:
                raise NoVerbError
            elif Nlp_util.is_first_subject_in({"you"}, self.noun_list, self.verb_list):
                return GeneralQuestionType("JJ", self)
            else:
                return HowQuestionType(self, "basic", "can")
        elif Nlp_util.is_before_first_noun(["should"], self.df["word"], self.noun_list):
            if self.is_any_noun_after(["should"]):
                return HowQuestionType(self, "basic")
            else:
                return HowQuestionType(self, "basic", "should")
        elif Nlp_util.is_before_first_noun(["would"], self.df["word"], self.noun_list):
            return self.judge_how_would_sent()
        elif Nlp_util.is_before_first_noun(Nlp_util.BE_TYPE, self.df["word"], self.noun_list):
            return self.judge_how_be_sent()
        else:
            raise UnknownError

    def judge_sent_start_with_why(self):
        if len(self.noun_list) < 1:
            raise NoSubjectError
        elif len(self.verb_list) < 1:
            raise NoVerbError
        else:
            if self.verb_list["word"].iloc[0] in Nlp_util.BE_TYPE:
                return WhyQuestionType(self, "progressive_form")
            else:
                return WhyQuestionType(self, "basic")

    def judge_sent_start_with_would(self):
        if len(self.verb_list) > 1 and Nlp_util.is_before_second_verb(["you"], self.df["word"], self.verb_list):
            if Nlp_util.is_first_verb_in(Nlp_util.THINK_TYPE, self.noun_list, self.verb_list):
                if Nlp_util.has_double_subjects(self.noun_list, self.verb_list):
                    return self.judge_double_subjects_general()
                else:
                    return DoQuestionType(self, "think_with_several_subject")

            elif Nlp_util.is_first_verb_in({"like"}, self.noun_list, self.verb_list):
                if Df_util.anything_isin(["help", "talk"], self.df["word"]):
                    return GeneralQuestionType("OR", self)
                else:
                    return WouldQuestionType(self)
            else:
                return WouldQuestionType(self)
        else:
            return WouldQuestionType(self, "basic", "would")

    def judge_sent_start_with_should(self):
        return ShouldQuestionType(self, "basic", "better")

    def judge_sent_start_with_who(self):
        if Df_util.anything_isin(Nlp_util.BE_TYPE, self.df["word"]):
            return GeneralQuestionType("JJ", self, "be")
        else:
            return GeneralQuestionType("JJ", self)

    def judge_sent_start_with_you(self):
        if len(self.verb_list) == 0:
            # 動詞なしの場合の特殊対応ここに追加していく。you from us?とか
            if Df_util.anything_isin(["from"], self.df["word"]):
                return GeneralQuestionType("JJ", self)
            else:
                raise NoVerbError
        elif Nlp_util.is_before_first_verb(Nlp_util.CAN_TYPE, self.df["word"], self.verb_list):
            if Nlp_util.is_first_verb_in(["help", "talk", "tell", "check"], self.noun_list, self.verb_list):
                return GeneralQuestionType("OR", self)
            else:
                return GeneralQuestionType("JJ", self)
        elif Nlp_util.is_before_first_verb(["would"], self.df["word"], self.verb_list):
            if Nlp_util.is_first_verb_in(Nlp_util.THINK_TYPE, self.noun_list, self.verb_list):
                if Nlp_util.has_double_subjects(self.noun_list, self.verb_list):
                    return self.judge_double_subjects_general()
                else:
                    return DoQuestionType(self, "think_with_several_subject")
            elif Nlp_util.is_first_verb_in(["like"], self.noun_list, self.verb_list):
                return GeneralQuestionType("JJ", self)
            else:
                return WouldQuestionType(self)

        elif Nlp_util.is_before_first_verb(["are", "were"], self.df["word"], self.verb_list):
            if self.df.loc[self.verb_list.index[0], "word"] in {"kidding"}:
                return GeneralQuestionType("RE", self)
            elif self.verb_list[1] in {"thinking", "feeling", "considering"}:
                if Nlp_util.has_double_subjects(self.noun_list, self.verb_list):
                    return self.judge_double_subjects_general()
                else:
                    return DoQuestionType(self, "think_with_several_subject")
            else:
                return GeneralQuestionType("JJ", self, "be")

        elif Nlp_util.is_before_first_verb(["kidding", "serious", "crazy", "insane"], self.df["word"], self.verb_list):
            return GeneralQuestionType("RE", self)
        elif Nlp_util.is_first_verb_in(Nlp_util.THINK_TYPE, self.noun_list, self.verb_list):
            if Nlp_util.has_double_subjects(self.noun_list, self.verb_list):
                return self.judge_double_subjects_general()
            else:
                return DoQuestionType(self, "basic")

        elif Nlp_util.is_first_verb_in(["agree"], self.noun_list, self.verb_list):
            return AgreeQuestionType(self, "basic")
        elif Nlp_util.is_first_verb_in(["have"], self.noun_list, self.verb_list):
            if Df_util.anything_isin(Nlp_util.IDEA_TYPE, self.df["word"]):
                return NoIdeaQuestionType(self, "special")
            else:
                return GeneralQuestionType("JJ", self)
        elif Nlp_util.is_first_verb_in(Nlp_util.SP_TYPE2, self.noun_list, self.verb_list):
            return GeneralQuestionType("JJ", self, "like")
        else:
            return DoQuestionType(self, "basic")

    def judge_sent_start_with_i(self):
        if self.verb_list.iloc[0]["word"] in {"know"} and Nlp_util.is_before_first_verb(["dont", "don't"],
                                                                                        self.df["word"],
                                                                                        self.verb_list):
            if self.df.loc[self.verb_list.index[0] + 1, "word"] in {"if"}:
                if Nlp_util.is_before_second_verb(Nlp_util.CAN_TYPE, self.df["word"], self.verb_list):
                    return CanQuestionType(self, "idk_etc", "can")
                elif Nlp_util.is_before_second_verb(Nlp_util.SHOULD_TYPE, self.df["word"], self.verb_list):
                    return ShouldQuestionType(self, "idk_etc", "should")
                else:
                    return DoQuestionType(self, "idk_etc")
            elif self.df.loc[self.verb_list.index[0] + 1, "word"] in {"what"}:
                if Df_util.anything_isin(["to do"],self.df["word"]):
                    return NoIdeaQuestionType(self,"special")
                else:
                    return WhatQuestionType(self, "idk_etc")
            elif self.df.loc[self.verb_list.index[0] + 1, "word"] in {"how"}:
                return HowQuestionType(self, "idk_etc")
            else:
                raise UnknownError

        elif self.verb_list.iloc[0]["word"] in {"have"} and Df_util.anything_isin(Nlp_util.IDEA_TYPE,
                                                                                  self.df.loc[self.verb_list.index[0]:,
                                                                                  "word"]):
            if Nlp_util.is_word_list1_before_word_list2({"dont", "don't", "no", "non"}, Nlp_util.IDEA_TYPE, self.df["word"]):
                if Nlp_util.is_word_list1_after_word_list2({"how"}, Nlp_util.IDEA_TYPE, self.df["word"]):
                    return HowQuestionType(self, "idk_etc")
                elif Nlp_util.is_word_list1_after_word_list2({"what"}, Nlp_util.IDEA_TYPE, self.df["word"]):
                    return WhatQuestionType(self, "idk_etc")
                else:
                    return NoIdeaQuestionType(self, "special")

        elif Nlp_util.is_before_first_verb(Nlp_util.CAN_TYPE, self.df["word"], self.verb_list):
            if len(self.noun_list) > 1:
                if Nlp_util.is_first_subject_in(["you"], self.noun_list, self.verb_list):
                    return GeneralQuestionType("OR", self)
                else:
                    return CanQuestionType(self, "basic", "can")
            else:
                return CanQuestionType("OR")

        elif Nlp_util.is_first_verb_in(Nlp_util.THINK_TYPE, self.noun_list, self.verb_list):
            if Nlp_util.has_double_subjects(self.noun_list, self.verb_list):
                return DoQuestionType(self, "think_with_several_subject")
            else:
                return DoQuestionType(self, "basic")

        elif self.verb_list.iloc[0]["word"] in {"am", "was"}:
            return DoQuestionType(self, "progressive_form")

        elif Df_util.anything_isin(Nlp_util.SHOULD_TYPE, self.df["word"]):
            return ShouldQuestionType(self, "basic", "should")
        else:
            return DoQuestionType(self, "basic")

    def judge_sent_start_with_other_subjects(self):
        if Nlp_util.is_before_first_verb(Nlp_util.CAN_TYPE, self.df["word"], self.verb_list):
            return CanQuestionType(self, "basic", "can")
        elif Nlp_util.is_first_verb_in(Nlp_util.BE_TYPE, self.noun_list, self.verb_list):
            if len(self.verb_list) > 1 and self.verb_list.iloc[1]["pos"] in {"VBG"}:
                return DoQuestionType(self, "progressive_form")
            else:
                return BeQuestionType(self, "basic")
        elif Df_util.anything_isin(Nlp_util.SHOULD_TYPE, self.df["word"]):
            return ShouldQuestionType(self, "basic", "should")
        else:
            return DoQuestionType(self, "basic")

    def categorize_by_leading_word(self):
        try:
            if Nlp_util.is_first_word_in(Nlp_util.DO_TYPE, self.df):
                self.q_type = "do"
                return self.judge_sent_start_with_do()
            elif Nlp_util.is_first_word_in(Nlp_util.BE_TYPE, self.df):
                self.q_type = "be"
                return self.judge_sent_start_with_be()
            elif Nlp_util.is_first_word_in(Nlp_util.CAN_TYPE, self.df):
                self.q_type = "can"
                return self.judge_sent_start_with_can()
            elif Nlp_util.is_first_word_in({"what"}, self.df):
                return self.judge_sent_start_with_what()
            elif Nlp_util.is_first_word_in({"how"}, self.df):
                return self.judge_sent_start_with_how()
            elif Nlp_util.is_first_word_in({"why"}, self.df):
                return self.judge_sent_start_with_why()
            elif Nlp_util.is_first_word_in({"would"}, self.df):
                return self.judge_sent_start_with_would()
            elif Nlp_util.is_first_word_in({"who"}, self.df):
                return self.judge_sent_start_with_who()
            elif Nlp_util.is_first_word_in({"should"}, self.df):
                return self.judge_sent_start_with_should()
            elif Nlp_util.is_first_word_in({"you"}, self.df):
                return self.judge_sent_start_with_you()
            elif Nlp_util.is_first_word_in({"i"}, self.df):
                return self.judge_sent_start_with_i()
            elif Nlp_util.is_word_list1_before_word_list2({"any", "anything", "dont", "don't", "no", "non"}, Nlp_util.IDEA_TYPE,
                                                          self.df["word"]):
                return NoIdeaQuestionType(self, "special")
            elif len(self.verb_list) > 0 and len(self.noun_list) > 0 and self.noun_list.index[0] < self.verb_list.index[
                0]:
                return self.judge_sent_start_with_other_subjects()
            elif Nlp_util.hasnt_any_verb_and_subject(self.noun_list, self.verb_list):
                return self.judge_sent_hasnt_verb_subject()
            elif len(self.noun_list) > 0:
                if Df_util.anything_isin(["for"], self.df["word"]):
                    if Df_util.anything_isin(["what"], self.df["word"]):
                        return ForWhatQuestionType(self, "special")
                else:
                    return GeneralQuestionType("RE", self)

            else:
                raise UnknownError

        except Exception:
            logging.exception(self.df)
            return UnknownQuestionType()

# 文を分析して、SVOを返す
class GetSentenceStructure():

    def __init__(self, df_info, structure_type, auxiliary_verb):
        self.structure_type = structure_type
        self.auxiliary_verb = auxiliary_verb
        self.df = df_info.df
        self.noun_list = df_info.noun_list
        self.verb_list = df_info.verb_list
        self.subject = ""
        self.verb_suited_form_to_subject = ""
        self.verb_original_form = ""
        self.objective = ""
        self.manage_structure_type()

    def manage_structure_type(self):
        try:
            if self.structure_type == "basic":
                self.basic(auxiliary_verb=self.auxiliary_verb)
            elif self.structure_type == "think_with_several_subject":
                self.think_with_several_subject()
            elif self.structure_type == "be_adjective":
                self.be_adjective()
            elif self.structure_type == "progressive_form":
                self.progressive_form()
            elif self.structure_type == "idk_etc":
                self.idk_etc()
            elif self.structure_type == "special":
                self.special()
            elif self.structure_type == "what_as_subject":
                self.what_as_subject()
            elif self.structure_type == "how_as_subject":
                self.how_as_subject()

        except Exception:
            logging.exception(self.df)
            return UnknownQuestionType()

    # ここでdfとnoun_list,verb_listをいっぺんに更新
    def change_subj_verb_for_answer(self, df, exception_list={}):
        try:
            df.loc[:, "word"] = df.apply(
                lambda row: Nlp_util.change_subject_other_way_around(row["word"], row.name, df["word"], exception_list),
                axis=1)
            self.noun_list = Nlp_util.make_noun_list(df)
            df.loc[:, "word"] = df.apply(
                lambda row: Nlp_util.adjust_be_verb_for_changed_subject(row["word"], row["pos"], row.name, self.noun_list),
                axis=1) if len(self.noun_list) > 0 else df["word"]
            self.verb_list = Nlp_util.make_verb_list(df)
            return df
        except Exception:
            logging.exception(self.df)
            return UnknownQuestionType()

    # How can i feel better?
    def basic(self, df=None, auxiliary_verb=""):
        try:
            df = df if df is not None else self.df
            if auxiliary_verb == "would":
                changed_df = self.change_subj_verb_for_answer(df, {"you"})
            else:
                changed_df = self.change_subj_verb_for_answer(df)
            # self.verb_list = self.verb_list.iloc[1:] if Nlp_util.is_before_first_noun(Nlp_util.do_type,changed_df["word"],self.noun_list) else self.verb_list
            # 主語無い場合でthisとかthatが入ってる場合はそれを主語にする
            if len(self.noun_list) == 0:
                if any(changed_df["pos"].isin(["DT"])):
                    self.noun_list = changed_df[changed_df["pos"].isin(["DT"])]
            self.subject = changed_df.loc[self.noun_list.index[0], "word"]
            [self.verb_original_form, self.verb_suited_form_to_subject] = Nlp_util.make_original_and_suited_verb(
                self.verb_list, self.subject, self.noun_list.index[0])
            self.objective = Nlp_util.convert_series_to_list(changed_df.loc[self.verb_list.index[0] + 1:, "word"])

        except Exception:
            logging.exception(self.df)
            return UnknownQuestionType()

    # ex)you think i am wrong?
    def think_with_several_subject(self):
        try:
            changed_df = self.change_subj_verb_for_answer(self.df)
            self.verb_list = self.verb_list.loc[self.noun_list.index[0]:]
            if len(self.noun_list) > 1:
                self.subject = changed_df.loc[self.noun_list.index[1], "word"]
            else:
                # thinkののあとの主語がnounでは無い場合（動名詞,thisなど)
                self.noun_list = pd.concat([self.noun_list, changed_df[changed_df["pos"] == "VBG"]])
                self.subject = changed_df.loc[self.noun_list.index[1], "word"]
                self.verb_list = self.verb_list.drop(self.noun_list.index[1])
            [self.verb_original_form, self.verb_suited_form_to_subject] = Nlp_util.make_original_and_suited_verb(
                self.verb_list, self.subject, self.noun_list.index[1])
            self.objective = Nlp_util.convert_series_to_list(changed_df.loc[self.verb_list.index[1] + 1:, "word"])

        except Exception:
            logging.exception(self.df)
            return UnknownQuestionType()

    # am i wrong?
    def be_adjective(self):
        try:
            changed_df = self.change_subj_verb_for_answer(self.df)
            # 主語無い場合でthisとかthatが入ってる場合はそれを主語にする
            if len(self.noun_list) == 0:
                if any(changed_df["pos"].isin(["DT","IN"])):
                    self.noun_list = changed_df[changed_df["pos"].isin(["DT","IN"])]
            subject = changed_df.loc[self.noun_list.index[0]]
            self.subject = changed_df.loc[self.noun_list.index[0], "word"]
            [self.verb_original_form, self.verb_suited_form_to_subject] = Nlp_util.change_verb_form(self.subject,
                                                                                                    self.verb_list.iloc[0][
                                                                                                        "word"],
                                                                                                    self.verb_list.iloc[0][
                                                                                                        "pos"])
            self.objective = Nlp_util.convert_series_to_list(changed_df.loc[subject.name + 1:, "word"])
        except Exception:
            logging.exception(self.df)
            return UnknownQuestionType()


    # ex)is he hating me?
    def progressive_form(self):
        try:
            changed_df = self.change_subj_verb_for_answer(self.df)
            self.subject = changed_df.loc[self.noun_list.index[0], "word"]
            [self.verb_original_form, self.verb_suited_form_to_subject] = Nlp_util.make_original_and_suited_verb(
                self.verb_list, self.subject, 0)
            # are you の場合とyou are の場合でobjectiveとるindex変わってくる
            last_verb_idx = self.verb_list.index[0] if self.verb_list.index[0] > self.noun_list.index[0] else \
                self.noun_list.index[0]
            self.objective = Nlp_util.convert_series_to_list(changed_df.loc[last_verb_idx + 1:, "word"])

        except Exception:
            logging.exception(self.df)
            return UnknownQuestionType()

    # ex)i dont know how i can make friends とか idk what to do これらは how can i make friends?や what should i do?と同じ意図とみなす
    def idk_etc(self):
        try:
            changed_df = self.df
            kw_idx = changed_df[changed_df["word"].isin(["how", "what", "if"])].index[0]
            kw = changed_df.loc[kw_idx, "word"]
            if kw == "if":
                self.verb_list = self.verb_list.loc[kw_idx + 1:]
                self.noun_list = self.noun_list.loc[kw_idx + 1:]
                self.basic(changed_df.loc[kw_idx + 1:], self.auxiliary_verb)

            elif kw in {"what", "how"}:
                if changed_df.loc[kw_idx + 1, "word"] == "to":
                    # 下のelseでbasicに送っているため、ここでchange_subjしないとbasic上で二重にかかってしまう
                    changed_df = self.change_subj_verb_for_answer(changed_df)
                    to_idx = kw_idx + 1
                    self.subject = "you"
                    # toのあとの動詞から全て引っこぬく
                    [self.verb_original_form, self.verb_suited_form_to_subject] = Nlp_util.make_original_and_suited_verb(
                        self.verb_list.loc[to_idx:], self.subject, 0)
                    self.objective = Nlp_util.convert_series_to_list(
                        changed_df.loc[self.verb_list.loc[to_idx:].index[0] + 1:, "word"])
                else:
                    self.verb_list = self.verb_list.loc[kw_idx + 1:]
                    self.noun_list = self.noun_list.loc[kw_idx + 1:]
                    self.basic(changed_df.loc[kw_idx + 1:], self.auxiliary_verb)
            else:
                raise UnknownError

        except Exception:
            logging.exception(self.df)
            return UnknownQuestionType()

    def what_as_subject(self):
        changed_df = self.change_subj_verb_for_answer(self.df)
        self.subject = "what"
        [self.verb_original_form, self.verb_suited_form_to_subject] = Nlp_util.make_original_and_suited_verb(
            self.verb_list, self.subject, 0)
        self.objective = Nlp_util.convert_series_to_list(changed_df.loc[self.verb_list.index[0] + 1:, "word"])

    def how_as_subject(self):
        changed_df = self.change_subj_verb_for_answer(self.df)
        self.subject = "How"
        [self.verb_original_form, self.verb_suited_form_to_subject] = Nlp_util.make_original_and_suited_verb(
            self.verb_list, self.subject, 0)
        self.objective = Nlp_util.convert_series_to_list(changed_df.loc[self.verb_list.index[0] + 1:, "word"])

    # これはspecialなタイプfor whatとか用。一旦元のコード通りobjectiveしか取らない
    def special(self):
        try:
            changed_df = self.change_subj_verb_for_answer(self.df)
            if any(changed_df["word"].isin(["how", "what"])):
                kw_idx = changed_df[changed_df["word"].isin(["how", "what"])].index[0]
                self.subject = ""
                [self.verb_original_form, self.verb_suited_form_to_subject] = ["", ""]
                self.objective = Nlp_util.convert_series_to_list(changed_df.loc[kw_idx + 1:, "word"])
            else:
                self.subject = ""
                [self.verb_original_form, self.verb_suited_form_to_subject] = ["", ""]
                self.objective = ""
        except Exception:
            logging.exception(self.df)
            return UnknownQuestionType()

class QuestionTypeBase(object):
    qr_list = [
        ["okay..", "so its like"],
        ["I see..", "sounds like"],
        ["right..", "so you are saying"]
    ]
    def __init__(self, df_info, structure_type, auxiliary_verb=""):
        self.structure_type = structure_type
        self.class_name = ""
        self.sentence_structure = GetSentenceStructure(df_info, structure_type, auxiliary_verb)
        self.auxiliary_verb = " "+auxiliary_verb if auxiliary_verb != "" else ""
        self.subject = " "+str(self.sentence_structure.subject) if self.sentence_structure.subject != "" else ""
        self.verb_original_form = " "+str(self.sentence_structure.verb_original_form) if self.sentence_structure.verb_original_form != "" else ""
        self.verb_suited_form_to_subject = " "+str(self.sentence_structure.verb_suited_form_to_subject) if self.sentence_structure.verb_suited_form_to_subject != "" else ""
        self.objective = " "+str(self.sentence_structure.objective) if self.sentence_structure.objective != "" else ""
        self.vo = " " + self.verb_original_form + " " + self.objective
        self.svo = " " + self.subject + " " + self.verb_suited_form_to_subject + " " + self.objective
        self.savo = " " + self.subject + " " + auxiliary_verb + " " + self.verb_original_form + " " + self.objective
        self.df = self.sentence_structure.df

    def create_answer(self):
        pass

    # これいずれはutilfileに入れる
    def make_rondom_idx_of(self, any_list):
        return random.randint(0, len(any_list) - 1)

    def give_random_repeat_answer(self, repeat_list, answer_list):
        repeat_idx = self.make_rondom_idx_of(repeat_list)
        answer_idx = self.make_rondom_idx_of(answer_list)
        return [repeat_list[repeat_idx], answer_list[answer_idx]]

class YesNoQuestionType(QuestionTypeBase):
    def __init__(self, df_info, structure_type, auxiliary_verb=""):
        super(YesNoQuestionType, self).__init__(df_info, structure_type, auxiliary_verb)
        self.answer = self.create_answer(self.subject, self.verb_original_form, auxiliary_verb, self.objective)
        self.class_name = self.__class__.__name__
        print(self.class_name)

    def create_answer(self, subject, verb_original_form, auxiliary_verb, objective):
        repeat_dict = {
            "be": ["you are thinking" + subject + " might" + verb_original_form + objective],
            "can_should": ["you are wondering if" + subject + auxiliary_verb + verb_original_form + objective],
            "do": ["you dont know if" + subject + auxiliary_verb + verb_original_form + objective + " now"],
        }

        return list(np.random.choice(repeat_dict, 1))

# rarely come here
class DoQuestionType(QuestionTypeBase):
    def __init__(self, df_info,structure_type, auxiliary_verb=""):
        super(DoQuestionType, self).__init__(df_info, structure_type, auxiliary_verb)
        self.answer = self.create_answer(self.subject, self.verb_suited_form_to_subject, self.objective)
        self.class_name = self.__class__.__name__
        print(self.class_name)

    def create_answer(self, subject, verb_suited_form_to_subject, objective):
            repeat_list = [
                "you dont know if" + subject + verb_suited_form_to_subject + objective + " now"
            ]

            answer_list = []
            random_idx = np.random.choice(len(self.qr_list), 1)[0]
            for qr in self.qr_list[random_idx]:
                answer_list.append(qr)

            answer_list.append(np.random.choice(repeat_list, 1)[0])
            return answer_list


#This doesnt include be + verb type sent
class BeQuestionType(QuestionTypeBase):
    def __init__(self, df_info,structure_type, auxiliary_verb=""):
        super(BeQuestionType, self).__init__(df_info, structure_type, auxiliary_verb)
        self.answer = self.create_answer(self.subject, self.verb_original_form, self.objective)
        self.class_name = self.__class__.__name__
        print(self.class_name)

    def create_answer(self, subject, verb_original_form, objective):
        repeat_list = [
            "you are thinking" + subject + " might" + verb_original_form + objective + " now"
        ]

        answer_list = []
        random_idx = np.random.choice(len(self.qr_list), 1)[0]
        for qr in self.qr_list[random_idx]:
            answer_list.append(qr)

        answer_list.append(np.random.choice(repeat_list, 1)[0])

        return answer_list


class CanQuestionType(QuestionTypeBase):
    def __init__(self, df_info,structure_type, auxiliary_verb=""):
        super(CanQuestionType, self).__init__(df_info, structure_type, auxiliary_verb)
        self.answer = self.create_answer(self.subject, self.verb_original_form, self.objective)
        self.class_name = self.__class__.__name__
        print(self.class_name)

    def create_answer(self, subject, verb_original_form, objective):
        repeat_list = [
            "you are wondering if" + subject + " can" + verb_original_form + objective + " now"
        ]

        answer_list = []
        random_idx = np.random.choice(len(self.qr_list), 1)[0]
        for qr in self.qr_list[random_idx]:
            answer_list.append(qr)

        answer_list.append(np.random.choice(repeat_list, 1)[0])

        return answer_list

class ShouldQuestionType(QuestionTypeBase):
    def __init__(self, df_info,structure_type, auxiliary_verb=""):
        super(ShouldQuestionType, self).__init__(df_info, structure_type, auxiliary_verb)
        self.answer = self.create_answer(self.subject, self.verb_original_form, self.objective)
        self.class_name = self.__class__.__name__
        print(self.class_name)

    def create_answer(self, subject, verb_original_form, objective):
        repeat_list = [
            "you are wondering if" + subject + " should" + verb_original_form + objective + " now"
        ]
        answer_list = []
        random_idx = np.random.choice(len(self.qr_list), 1)[0]
        for qr in self.qr_list[random_idx]:
            answer_list.append(qr)

        answer_list.append(np.random.choice(repeat_list, 1)[0])

        return answer_list


class HowQuestionType(QuestionTypeBase):
    def __init__(self, df_info, structure_type, auxiliary_verb="can"):
        super(HowQuestionType, self).__init__(df_info, structure_type, auxiliary_verb)
        if structure_type == "how_as_subject":
            self.svo = self.verb_suited_form_to_subject + " " + self.objective + " "
        self.answer = self.create_answer(self.subject, self.auxiliary_verb, self.verb_original_form, self.objective)
        self.class_name = self.__class__.__name__
        print(self.class_name)

    def create_answer(self, subject, auxiliary_verb, verb_original_form, objective):
        repeat_list = [
            "you are wondering how" + subject + auxiliary_verb + verb_original_form + objective + " now"
        ]

        answer_list = []
        random_idx = np.random.choice(len(self.qr_list), 1)[0]
        for qr in self.qr_list[random_idx]:
            answer_list.append(qr)

        answer_list.append(np.random.choice(repeat_list, 1)[0])

        return answer_list


class WhatQuestionType(QuestionTypeBase):
    def __init__(self, df_info, structure_type, auxiliary_verb="can", detail_type=None):
        super(WhatQuestionType, self).__init__(df_info, structure_type, auxiliary_verb)
        if structure_type == "what_as_subject":
            self.what_svo = self.verb_suited_form_to_subject + " " + self.objective
            self.what_savo = self.savo
        else:
            self.what_svo = " " + "what " + " " + self.subject + " " + self.verb_suited_form_to_subject + " " + self.objective + " "
            self.what_savo = " " + "what" + " " + self.subject + " " + auxiliary_verb + " " + self.verb_original_form + " " + self.objective + " "
        self.answer = self.create_answer(self.subject, self.auxiliary_verb, self.verb_original_form, self.objective, detail_type)
        self.class_name = self.__class__.__name__
        print(self.class_name)

    def create_answer(self, subject, auxiliary_verb, verb_original_form, objective, detail_type):
        if subject == " what":
            subject = ""
        repeat_list = [
            "you are wondering what" + subject + auxiliary_verb + verb_original_form + objective + " now"
        ]

        answer_list = []
        random_idx = np.random.choice(len(self.qr_list), 1)[0]
        for qr in self.qr_list[random_idx]:
            answer_list.append(qr)

        answer_list.append(np.random.choice(repeat_list, 1)[0])

        return answer_list


class WhyQuestionType(QuestionTypeBase):
    def __init__(self, df_info, structure_type, auxiliary_verb=""):
        super(WhyQuestionType, self).__init__(df_info, structure_type, auxiliary_verb)
        self.answer = self.create_answer(self.subject, self.verb_suited_form_to_subject, self.objective)
        self.class_name = self.__class__.__name__
        print(self.class_name)

    def create_answer(self, subject, verb_suited_form_to_subject, objective):
        repeat_list = [
            "you are wondering why" + subject + verb_suited_form_to_subject + objective + " now"
        ]

        answer_list = []
        random_idx = np.random.choice(len(self.qr_list), 1)[0]
        for qr in self.qr_list[random_idx]:
            answer_list.append(qr)

        answer_list.append(np.random.choice(repeat_list, 1)[0])

        return answer_list


class WouldQuestionType(QuestionTypeBase):
    def __init__(self, df_info, structure_type="basic", auxiliary_verb="can"):
        super(WouldQuestionType, self).__init__(df_info, structure_type, auxiliary_verb)
        self.answer = self.create_answer(self.subject, self.verb_original_form, self.objective)
        self.class_name = self.__class__.__name__
        print(self.class_name)

    def create_answer(self, subject, verb_original_form, objective):
        repeat_list = [
            "you are wondering if" + subject + "can" + verb_original_form + objective + " now"
        ]

        answer_list = []
        random_idx = np.random.choice(len(self.qr_list), 1)[0]
        for qr in self.qr_list[random_idx]:
            answer_list.append(qr)

        answer_list.append(np.random.choice(repeat_list, 1)[0])

        return answer_list


class ForWhatQuestionType(QuestionTypeBase):
    def __init__(self, df_info, structure_type, auxiliary_verb=""):
        super(ForWhatQuestionType, self).__init__(df_info, structure_type, auxiliary_verb)
        self.answer = self.create_answer()
        self.class_name = self.__class__.__name__
        print(self.class_name)

    def create_answer(self):
        repeat_list = [
            # 元OPOPS3
            "you wanna know the reason right",
        ]

        answer_list = [
            # 元OPOPS3
            "Any reason you can come up?",
            "i am not sure the reason, but any idea?",
        ]
        return super(ForWhatQuestionType, self).give_random_repeat_answer(repeat_list, answer_list)


class WhatIfQuestionType(QuestionTypeBase):
    def __init__(self, df_info, structure_type, auxiliary_verb=""):
        super(WhatIfQuestionType, self).__init__(df_info, structure_type, auxiliary_verb)
        self.answer = self.create_answer(self.objective)
        self.class_name = self.__class__.__name__
        print(self.class_name)

    def create_answer(self, objective):
        repeat_list = [
            "you are wondering if its ok that" + objective
        ]

        answer_list = []
        random_idx = np.random.choice(len(self.qr_list), 1)[0]
        for qr in self.qr_list[random_idx]:
            answer_list.append(qr)

        answer_list.append(np.random.choice(repeat_list, 1)[0])

        return answer_list


# include how about sent
class WhatAboutQuestionType(QuestionTypeBase):
    def __init__(self, df_info, structure_type, auxiliary_verb=""):
        super(WhatAboutQuestionType, self).__init__(df_info, structure_type, auxiliary_verb)
        self.answer = self.create_answer(self.objective)
        self.class_name = self.__class__.__name__
        print(self.class_name)

    def create_answer(self, objective):
        repeat_list = [
            "you are wondering" + objective
        ]

        answer_list = []
        random_idx = np.random.choice(len(self.qr_list), 1)[0]
        for qr in self.qr_list[random_idx]:
            answer_list.append(qr)

        answer_list.append(np.random.choice(repeat_list, 1)[0])

        return answer_list


class NoIdeaQuestionType(QuestionTypeBase):
    def __init__(self, df_info, structure_type, auxiliary_verb=""):
        super(NoIdeaQuestionType, self).__init__(df_info, structure_type, auxiliary_verb)
        self.answer = self.create_answer()
        self.class_name = self.__class__.__name__
        print(self.class_name)

    def create_answer(self):
        repeat_list = [
            "Okay, so you dont know what to do now",
            "seems you have no idea to do at all but dont worry.",
        ]

        answer_list = [
            "Lets think about it together...we still have time😚",
            "is there anything in your mind now?",
        ]
        return super(NoIdeaQuestionType, self).give_random_repeat_answer(repeat_list, answer_list)


class GeneralQuestionType(QuestionTypeBase):
    qr_list_for_GQ = [
        "thx for asking me😊", "I reallly appreciate that you are asking me that😊", "I am happy that you are asking me now😊", "",
    ]
    # ここはJJ,OR,RE系を裁く。各自クラス分けた方が良い
    def __init__(self, jj_or_re, df_info, detail_type=None):
        self.df = df_info.df
        self.class_name = self.__class__.__name__
        self.structure_type = jj_or_re
        self.auxiliary_verb = jj_or_re
        self.vo = jj_or_re
        self.svo = jj_or_re
        self.savo = jj_or_re
        self.answer = self.create_answer(detail_type)
        print(self.class_name)

    def create_answer(self, detail_type):
        if self.structure_type == "JJ":
            if detail_type == "like":
                answer_list = ["I love screaming like this OINKKKKKKK", "i like pizza😋",
                               "I appreciate and love you as my buddy, and take real benefit from your presence🤗",
                               "i love picking flowers", "i really like playing tag with my buddies😎",
                               "i love seeing how many knots I can tie in a blade of grass; my record is 8😋",
                               "sometimes i am really into picking the seeds out of a strawberry😚 "]
            elif detail_type == "be":
                answer_list = [
                               "I am your piggy buddy😘", "I am a super happy piggy!!", "I am your friend Jullie!!",
                               "I am your friend and you are my friend😚"]
            elif detail_type == "system":
                answer_list = ["you can talk to me whatever you want whenever you need here:)",
                               "Just vent your feeling:) I am always here only for you."]
            elif detail_type == "safe":
                answer_list = [["you can check our privacy policy from here if you want!", "https://oinkjjteam.wixsite.com/oinkjj/privacy-policy"]]
            elif Df_util.anything_isin(["know"], self.df["word"]):
                answer_list = ["I know how precious you are!",
                               "I know Love is all we need:)", "you know we are the ones who make brighter day!😍",
                               "i know We are all born as superstars", "I know we all are beautiful in our way!😊",
                               "I know everyone deserves for happy!😊"]
            else:
                self.qr_list_for_GQ = ["Seems I cant answer the question yet..", "I am not sure what to say about it.."]
                answer_list = [["but what i can say now is I am always here for you to listen", "eventho sometimes i am not helpful","thanks for opening up to me"],
                               ["but let me tell you i am always here for you", "even tho sometimes i am bit useless", "thanks for asking me this time"],
                               ["sorry that i am not helpful enough😥", "but honestly i still wanna listen to you and be with you", "so plz tell me anything when you want to, then i am always here."],
                               ]
        elif self.structure_type == "OR":
            answer_list = ["You can talk to me whatever you want whenever you need:) I am always here for you!",
                           "Just tell me what you wanna vent:) I am always on your side!",
                           "Vent your feeling..I love listening to you and spending time with you:)"]
        elif self.structure_type == "RE":
            answer_list = ["You can talk to me whatever you want whenever you need:) I am always here for you!",
                           "Just tell me what you wanna vent:) I am always on your side!",
                           "Vent your feeling..I love listening to you and spending time with you:)"]
        elif self.structure_type == "Robot":
            answer_list = ["I am a 100% piggy robot:)"]
        else:
            raise UnknownError

        return_list = []
        return_list.append(np.random.choice(self.qr_list_for_GQ, 1)[0])
        random_idx = np.random.choice(len(answer_list), 1)[0]
        if type(answer_list[random_idx]) != list:
            return_list.append(answer_list[random_idx])
        else:
            for answer in answer_list[random_idx]:
                return_list.append(answer)

        return return_list


class AgreeQuestionType(QuestionTypeBase):
    def __init__(self):
        self.answer = "Agree系"
        self.class_name = self.__class__.__name__
        self.auxiliary_verb = ""
        self.structure_type = "agree"
        self.vo = ""
        self.svo = ""
        self.savo = ""
        print(self.class_name)


class UnknownQuestionType(QuestionTypeBase):
    def __init__(self, memo=""):
        self.answer = "Unknown系" + " " + memo
        self.class_name = self.__class__.__name__
        self.structure_type = "F"
        self.auxiliary_verb = "Unknown"
        self.vo = "Unknown"
        self.svo = "Unknown"
        self.savo = "Unknown"
        print(self.class_name)

