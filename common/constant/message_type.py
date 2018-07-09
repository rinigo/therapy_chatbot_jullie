"""
AP = appriciation CMP=compassion CQD= closed question detail CR = care ENC = encourage
OQD = opened question detail OYS = on your side OQFL = open question feeling, LIS = Listening
"""
from enum import Enum


class MessageType(Enum):
    INTRO = '0'

    SUICIDE = 'suicide'

    UNIMPORTANT = 'unimportant'

    QUESTION = 'question'

    QR = 'qr'
    REPEAT = 'repeat'
    LABELING = 'labeling'
    CQL = 'cql'
    SPECIAL = 'special'
    AP = 'AP'
    CMP = 'CMP'
    CQD = 'CQD'
    CR = 'CR'
    ENC = 'ENC'
    OQD = 'OQD'
    OYS = 'OYS'
    LIS = "LIS"
    OQFL = 'OQFL'
    REACTION = 'reaction'
    HATE_REPEATITIVE = 'hate_repeatitive'
    JULLIE_USELESS = 'jullie_useless'
    NO_IDEA = "no_idea"
    LACK_OF_CONFIDENCE = "lack_of_confidence"
    COMPLAINT_OR_DISSING = "compalint_or_dissing"
    QUESTION_NO_IDEA = "question_no_idea"
    GENERAL_QUESTION_TYPE = "general_question_type"
    OYS_AFTER_CMP = "oys_after_cmp"
    CMP_FOR_PREVIOUS_SENT = "cmp_for_previous_sent"
    ASK_TO_FINISH = "ask_to_finish"
    OYS_AFTER_REPEAT = "oys_after_repeat"
    NOT_LISTENING = 'not_listening'
    NEED_HELP = 'need_help'
    CANT_GET_ATTENTION_FROM_BF = "cant_get_attention_from_bf"
    LIKE_SOMEONE = "like_someone"
    ABOUT_BREAKUP = "about_breakup"
    NO_FRIENDS = "no_friends"
    OYS_MEANINGLESS_IN_A_ROW = "oys_meaningless_in_a_row"
    BOTH_CMP_AND_REPEAT = "both_cmp_and_repeat"


    reaction_type_list = [SPECIAL, AP, CMP, CQD, CR, ENC, OYS, OQFL, OQD]

    # session-related
    ASK_NEW_SESSION = '1'
    ASK_COMMENT = '2'
    ASK_MOOD = '3'
    ENDED_SESSION = '4'
    ASK_MOOD_REMIND = '5'
    ASK_NEW_SESSION_REMIND = '6'
    SESSION_PREPARED = '8'

    ADMIN = '7'

    ASK_FEED_BACK = '9'

    QR_UNNEEDED = [ASK_TO_FINISH, OYS_AFTER_CMP, UNIMPORTANT, OYS_MEANINGLESS_IN_A_ROW, ABOUT_BREAKUP, LIKE_SOMEONE, LACK_OF_CONFIDENCE, CANT_GET_ATTENTION_FROM_BF, NO_FRIENDS]

    ANXIOUS = 'anxious'
    LONELY = 'lonely'
    CALL_ME_NAMES = 'call_me_names'
    MONEY = 'money'
    MISSING = 'missing'