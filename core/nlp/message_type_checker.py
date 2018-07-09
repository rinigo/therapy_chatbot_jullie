import logging
import models
from common.constant.intent_type import Intent
from common.constant.user_status import UserStatus
from common.constant.message_type import MessageType as MsgType
from common.util.util import deduplicate_preserving_order
from core.nlp.normalizer.message_normalizer import MessageNormalizer
from core.nlp.suicide.suicide_detector import SuicideDetector
from common.word_format.df_utils import Nlp_util
from common.constant.df_from_csv import WORD_LIST_FOR_CMP
from common.word_format.word_formatter import WordFormatter


class MessageTypeChecker:
    def __init__(self, user, msg):
        self.user = user
        self.msg = msg

    def __call__(self):
        try:
            if self.user.status == UserStatus.SUICIDE_IN_SESSION.value:
                return [MsgType.SUICIDE.value]

            elif SuicideDetector.is_suicidal(self.msg.text_df):
                message_type = [MsgType.SUICIDE.value]
                return message_type

            elif self.__is_in_intent_list(Intent.CANT_GET_ATTENTION_FROM_BF):
                message_type = [MsgType.CANT_GET_ATTENTION_FROM_BF.value]

            elif self.__is_in_intent_list(Intent.LIKE_SOMEONE):
                message_type = [MsgType.LIKE_SOMEONE.value]

            elif self.__is_in_intent_list(Intent.LACK_OF_CONFIDENCE):
                message_type = [MsgType.LACK_OF_CONFIDENCE.value]

            elif self.__is_in_intent_list(Intent.ABOUT_BREAKUP):
                message_type = [MsgType.ABOUT_BREAKUP.value]

            elif self.__is_in_intent_list(Intent.NO_FRIENDS):
                message_type = [MsgType.NO_FRIENDS.value]

            elif self.__is_in_intent_list(Intent.NOT_LISTENING):
                message_type = [MsgType.NOT_LISTENING.value]

            elif self.__is_in_intent_list(Intent.HATE_REPETITIVE):
                message_type = [MsgType.HATE_REPEATITIVE.value]

            elif self.__is_in_intent_list(Intent.JULLIE_USELESS):
                message_type = [MsgType.JULLIE_USELESS.value]

            elif self.__is_in_intent_list(Intent.COMPLAINT_OR_DISSING):
                message_type = [MsgType.COMPLAINT_OR_DISSING.value]

            elif self.__is_in_intent_list(Intent.NO_IDEA):
                message_type = [MsgType.NO_IDEA.value]

            elif self.__is_in_intent_list(Intent.QUESTION_NO_IDEA):
                message_type = [MsgType.QUESTION_NO_IDEA.value]

            elif self.__is_in_intent_list(Intent.NEED_HELP):
                message_type = [MsgType.NEED_HELP.value]

            elif self.__is_in_intent_list(Intent.ANXIOUS):
                message_type = [MsgType.ANXIOUS.value]

            elif self.__is_in_intent_list(Intent.LONELY):
                message_type = [MsgType.LONELY.value]

            elif self.__is_in_intent_list(Intent.CALL_ME_NAMES):
                message_type = [MsgType.CALL_ME_NAMES.value]

            elif self.__is_in_intent_list(Intent.MONEY):
                message_type = [MsgType.MONEY.value]

            elif self.__is_in_intent_list(Intent.MISSING):
                message_type = [MsgType.MISSING.value]

            elif self.__has_intent_from_api_only(self.msg.intent_list):
                message_type = self.__get_msg_type_of_api_intent_only()

            elif self.__has_question_only(self.msg.intent_list):
                message_type = self.__get_question_message_type(self.msg.intent_list)

            elif self.__is_msg_meaningless_intent_only(self.msg.intent_list):
                message_type = self.__get_msg_type_for_only_meaningless_intent(self.user.id)

            else:
                message_type = self.__get_regular_message_type()

            if self.__exists_bye_intent():
                message_type = self.__modify_message_types_by_bye_intents(message_type)

            message_type = self.__add_QR_by_past_response_types(message_type)

            message_type = deduplicate_preserving_order(message_type)

            return message_type
        except:
            logging.exception('')
            return [MsgType.LIS.value]

    def __get_regular_message_type(self):
        try:
            normal_intents_idx_list = [idx for idx, i in enumerate(self.msg.intent_list) if i == Intent.NORMAL]
            normal_intents_df = self.msg.text_df[self.msg.text_df.sidx.isin(normal_intents_idx_list)]

            message_type = self.__make_cmp_or_repeat(self.user.id, normal_intents_df)

            if Intent.LONG_MSGs in self.msg.intent_list and MsgType.CMP.value in message_type:
                message_type = [MsgType.BOTH_CMP_AND_REPEAT.value]

            return message_type
        except:
            logging.exception('')
            return []

    def __exists_bye_intent(self):
        try:
            return any(i.value in Intent.BYE_INTENTS.value for i in self.msg.intent_list)
        except:
            logging.exception('')
            return False

    def __modify_message_types_by_bye_intents(self, message_type):
        try:
            types_uncompatible_with_bye_intents = \
                [MsgType.LABELING.value, MsgType.CQL.value] + MsgType.reaction_type_list.value

            message_type = [i for i in message_type if i not in types_uncompatible_with_bye_intents]

            return message_type
        except:
            logging.exception('')
            return message_type

    def __add_QR_by_past_response_types(self, message_type_list):
        try:
            if any(message_type in MsgType.QR_UNNEEDED.value for message_type in message_type_list):
                return message_type_list

            past_3_response_types = models.Response.find_past_3_response_types(self.user.id)

            exists_recent_QR = MsgType.QR.value in past_3_response_types
            exists_strong_negative = any([i <= -150 for i in
                                          self.msg.sentiment_score_df.nscore.values]) if self.msg.sentiment_score_df.nscore is not None else False

            if not exists_recent_QR or exists_strong_negative:
                message_type_list.insert(0, MsgType.QR.value)

            return message_type_list
        except:
            logging.exception('')
            return message_type_list

    @staticmethod
    def __make_cmp_or_repeat(user_id, text_df):
        if MessageTypeChecker.__is_cmp_makeable(text_df, user_id):
            return [MsgType.CMP.value]
        else:
            return [MsgType.REPEAT.value]

    @classmethod
    def __is_cmp_makeable(cls, text_df, user_id):
        try:
            last_response_type_list = models.Response.fetch_last_response_type_list(user_id)
            print("\nLast response type\n{}".format(last_response_type_list))

            if MsgType.CMP.value in last_response_type_list:
                return False

            if any(text_df.base_form.isin(WORD_LIST_FOR_CMP.word.tolist())):
                return True
            else:
                return False

        except:
            logging.exception('')
            return False

    def __is_in_intent_list(self, intent):
        try:
            return intent in self.msg.intent_list
        except:
            logging.exception('')
            return False

    @staticmethod
    def __has_intent_from_api_only(intents):
        try:
            if all(i == Intent.MEANINGLESS for i in intents):
                return False
            elif all(i.value in
                     Intent.UNIMPORTANT_1.value + Intent.UNIMPORTANT_2.value + [Intent.MEANINGLESS.value]
                     for i in intents):
                return True
            else:
                return False

        except:
            logging.exception('')
            return False

    @staticmethod
    def __get_msg_type_of_api_intent_only():
        return [MsgType.UNIMPORTANT.value]

    @classmethod
    def __is_msg_meaningless_intent_only(cls, intents):
        return True if all(i in {Intent.MEANINGLESS, Intent.UnknownQuestionType} for i in intents) else False

    @classmethod
    def __is_previous_msg_cmp_makeable(cls, user_id):
        try:
            previous_msg = models.Message.fetch_previous_msg(user_id)
            if len(previous_msg) == 0:
                return False

            w_toks = WordFormatter.SToks2WToks([previous_msg])

            message_normalizer = MessageNormalizer()
            df = message_normalizer(w_toks, None, from_preprocessor=False)

            target_pos = Nlp_util.pos_VERBs + Nlp_util.pos_ADVERBs + Nlp_util.pos_ADJECTIVEs
            target_word_df = df[df.pos.isin(target_pos)]

            if any(target_word_df.base_form.isin(WORD_LIST_FOR_CMP.word.tolist())):
                return True
            else:
                return False
        except:
            logging.exception('')
            return False

    @classmethod
    def __get_msg_type_for_only_meaningless_intent(cls, user_id):
        previous_response_type = models.Response.fetch_previous_msg_response_type(user_id)
        print("\nPrevious response type\n{}".format(previous_response_type))

        if len(previous_response_type) == 0 or previous_response_type is None:
            message_type = [MsgType.OYS_AFTER_REPEAT.value]

        # keep this first two orders
        elif any(i == MsgType.CMP.value for i in previous_response_type):
            message_type = [MsgType.OYS_AFTER_CMP.value]

        # TODO ここはAsk to finishのところでyes noどっちなのかってのも判別したい
        elif any(i in [MsgType.OYS_AFTER_REPEAT.value, MsgType.ASK_TO_FINISH.value] for i in previous_response_type):
            message_type = [MsgType.OYS_MEANINGLESS_IN_A_ROW.value]

        # TODO　前回がmeaningless以外の場合全部この下の対応でいいと思う。 QRのとことかいらない。
        else:
            if cls.__is_previous_msg_cmp_makeable(user_id):
                message_type = [MsgType.CMP_FOR_PREVIOUS_SENT.value]
            else:
                total_number_of_msg_in_session = models.Message.count_total_msg_in_session(user_id)

                if total_number_of_msg_in_session > 20:
                    message_type = [MsgType.ASK_TO_FINISH.value]
                else:
                    message_type = [MsgType.OYS_AFTER_REPEAT.value]

        return message_type

    @staticmethod
    def __has_question_only(intents):
        # except UnknownQuestionType. its regarded as meaningless
        try:
            exists_question = any(
                i.value in Intent.PROPER_QUESTION_TYPES.value + [Intent.QUESTION_GENERAL_TYPE.value] for i in intents)

            # TODO is this correct? if so, change the func and vars names
            c2 = all(
                i.value in Intent.PROPER_QUESTION_TYPES.value + [Intent.MEANINGLESS.value,
                                                                 Intent.QUESTION_GENERAL_TYPE.value,
                                                                 Intent.CALL_JULLIE.value, Intent.HAHA.value,
                                                                 Intent.STICKER.value]
                + Intent.UNIMPORTANT_1.value + Intent.UNIMPORTANT_2.value for i in intents)

            if exists_question and c2:
                return True
            else:
                return False
        except:
            logging.exception('')
            return False

    @staticmethod
    def __get_question_message_type(intents):
        if Intent.QUESTION_GENERAL_TYPE in intents:
            message_type = [MsgType.GENERAL_QUESTION_TYPE.value]
        else:
            message_type = [MsgType.QUESTION.value]

        # NORMAL_AND_UNIMOPRTANT[:-1] = any intent except normal
        if any(i.value in Intent.NORMAL_AND_UNIMPORTANT.value[:-1] for i in intents):
            message_type.append(MsgType.UNIMPORTANT.value)

        return message_type
