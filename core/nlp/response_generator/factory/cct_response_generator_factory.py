import logging
from common.constant.message_type import MessageType as MsgType
from core.nlp.response_generator.product.cct.OYS_Meaningless_In_A_Row_response_generator import \
    OYSMeaninglessInARowResponseGenerator
from core.nlp.response_generator.factory.base_response_generator_factory import BaseResponseGeneratorFactory
from core.nlp.response_generator.product.cct.CQL_response_generator import CQLResponseGenerator
from core.nlp.response_generator.product.cct.LIS_response_generator import LISResponseGenerator
from core.nlp.response_generator.product.cct.OYS_CMP_response_generator import OYSCMPResponseGenerator
from core.nlp.response_generator.product.cct.about_breakup_response_generator import AboutBreakupResponseGenerator
from core.nlp.response_generator.product.cct.anxious_response_generator import AnxiousResponseGenerator
from core.nlp.response_generator.product.cct.ask_finish_response_generator import AskFinishResponseGenerator
from core.nlp.response_generator.product.cct.bf_attention_response_generator import BfAttentionResponseGenerator
from core.nlp.response_generator.product.cct.bot_useless_response_generator import BotUselessResponseGenerator
from core.nlp.response_generator.product.cct.call_me_names_response_generator import CallMeNamesResponseGenerator
from core.nlp.response_generator.product.cct.cmp_response_generator import CMPResponseGenerator
from core.nlp.response_generator.product.cct.disrespect_response_generator import DisrespectResponseGenerator
from core.nlp.response_generator.product.cct.general_question_response_generator import GeneralQuestionResponseGenerator
from core.nlp.response_generator.product.cct.labeling_response_generator import LabelingResponseGenerator
from core.nlp.response_generator.product.cct.lack_confidence_response_generator import LackConfidenceResponseGenerator
from core.nlp.response_generator.product.cct.like_someone_response_generator import LikeSomeoneResponseGenerator
from core.nlp.response_generator.product.cct.lonely_response_generator import LonelyResponseGenerator
from core.nlp.response_generator.product.cct.missing_response_generator import MissingResponseGenerator
from core.nlp.response_generator.product.cct.money_response_generator import MoneyResponseGenerator
from core.nlp.response_generator.product.cct.need_help_response_generator import NeedHelpResponseGenerator
from core.nlp.response_generator.product.cct.no_idea_response_generator import NoIdeaResponseGenerator
from core.nlp.response_generator.product.cct.not_listening_response_generator import NotListeningResponseGenerator
from core.nlp.response_generator.product.cct.oys_repeat_response_generator import OYSRepeatResponseGenerator
from core.nlp.response_generator.product.cct.previous_sent_cmp_response_generator import \
    PreviousSentCMPResponseGenerator
from core.nlp.response_generator.product.cct.question_no_idea_response_generator import QuestionNoIdeaResponseGenerator
from core.nlp.response_generator.product.cct.question_response_generator import QuestionResponseGenerator
from core.nlp.response_generator.product.cct.quick_response_generator import QuickResponseGenerator
from core.nlp.response_generator.product.cct.reaction_response_generator import ReactionResponseGenerator
from core.nlp.response_generator.product.cct.repeat_response_generator import RepeatResponseGenerator
from core.nlp.response_generator.product.cct.repetitive_response_generator import RepetitiveResponseGenerator
from core.nlp.response_generator.product.cct.suicide_response_generator import SuicideResponseGenerator
from core.nlp.response_generator.product.cct.unimportant_response_generator import UnimportantResponseGenerator
from core.nlp.response_generator.product.cct.no_friends_response_generator import ForNoFriendsResponseGenerator
from core.nlp.response_generator.product.reflection.ask_feedback_response_generator import AskFeedbackResponseGenerator
from core.nlp.response_generator.product.cct.both_cmp_and_repeat_generator import BothCmpANdRepeatResponseGenerator


class UnknownError:
    pass


class CCTResponseGeneratorFactory(BaseResponseGeneratorFactory):
    @staticmethod
    def create(user, message, msg_type):
        try:
            print('\nmessage_type:\n', msg_type)
            args = user, message, msg_type

            if msg_type == MsgType.SUICIDE.value:
                return SuicideResponseGenerator(*args)
            elif msg_type == MsgType.QUESTION.value:
                return QuestionResponseGenerator(*args)
            elif msg_type == MsgType.QR.value:
                return QuickResponseGenerator(*args)
            elif msg_type == MsgType.REPEAT.value:
                return RepeatResponseGenerator(*args)
            elif msg_type == MsgType.CMP.value:
                return CMPResponseGenerator(*args)
            elif msg_type == MsgType.NO_FRIENDS.value:
                return ForNoFriendsResponseGenerator(*args)
            elif msg_type == MsgType.CMP_FOR_PREVIOUS_SENT.value:
                return PreviousSentCMPResponseGenerator(*args)
            elif msg_type == MsgType.ASK_TO_FINISH.value:
                return AskFinishResponseGenerator(*args)
            elif msg_type == MsgType.OYS_AFTER_REPEAT.value:
                return OYSRepeatResponseGenerator(*args)
            elif msg_type == MsgType.OYS_AFTER_CMP.value:
                return OYSCMPResponseGenerator(*args)
            elif msg_type == MsgType.LABELING.value:
                return LabelingResponseGenerator(*args)
            elif msg_type == MsgType.CQL.value:
                return CQLResponseGenerator(*args)
            elif msg_type in MsgType.reaction_type_list.value:
                return ReactionResponseGenerator(*args)
            elif msg_type in MsgType.LIS.value:
                return LISResponseGenerator(*args)
            elif msg_type == MsgType.HATE_REPEATITIVE.value:
                return RepetitiveResponseGenerator(*args)
            elif msg_type == MsgType.JULLIE_USELESS.value:
                return BotUselessResponseGenerator(*args)
            elif msg_type == MsgType.NOT_LISTENING.value:
                return NotListeningResponseGenerator(*args)
            elif msg_type == MsgType.NO_IDEA.value:
                return NoIdeaResponseGenerator(*args)
            elif msg_type == MsgType.QUESTION_NO_IDEA.value:
                return QuestionNoIdeaResponseGenerator(*args)
            elif msg_type == MsgType.GENERAL_QUESTION_TYPE.value:
                return GeneralQuestionResponseGenerator(*args)
            elif msg_type == MsgType.NEED_HELP.value:
                return NeedHelpResponseGenerator(*args)
            elif msg_type == MsgType.COMPLAINT_OR_DISSING.value:
                return DisrespectResponseGenerator(*args)
            elif msg_type == MsgType.UNIMPORTANT.value:
                return UnimportantResponseGenerator(*args)
            elif msg_type == MsgType.CANT_GET_ATTENTION_FROM_BF.value:
                return BfAttentionResponseGenerator(*args)
            elif msg_type == MsgType.LIKE_SOMEONE.value:
                return LikeSomeoneResponseGenerator(*args)
            elif msg_type == MsgType.LACK_OF_CONFIDENCE.value:
                return LackConfidenceResponseGenerator(*args)
            elif msg_type == MsgType.ABOUT_BREAKUP.value:
                return AboutBreakupResponseGenerator(*args)
            elif msg_type == MsgType.ASK_FEED_BACK.value:
                return AskFeedbackResponseGenerator(*args)
            elif msg_type == MsgType.OYS_MEANINGLESS_IN_A_ROW.value:
                return OYSMeaninglessInARowResponseGenerator(*args)
            elif msg_type == MsgType.ANXIOUS.value:
                return AnxiousResponseGenerator(*args)
            elif msg_type == MsgType.LONELY.value:
                return LonelyResponseGenerator(*args)
            elif msg_type == MsgType.CALL_ME_NAMES.value:
                return CallMeNamesResponseGenerator(*args)
            elif msg_type == MsgType.MONEY.value:
                return MoneyResponseGenerator(*args)
            elif msg_type == MsgType.BOTH_CMP_AND_REPEAT.value:
                return BothCmpANdRepeatResponseGenerator(*args)

            elif msg_type == MsgType.MISSING.value:
                return MissingResponseGenerator(*args)
            else:
                raise UnknownError
        except:
            logging.exception('Unknown Message Type is Found')
