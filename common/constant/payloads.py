from enum import Enum


class Payload(Enum):
    MESSAGE_WITHOUT_BUTTON_IN_INTRO = 'MESSAGE_WITHOUT_BUTTON_IN_INTRO_PAYLOAD'

    SUICIDAL_THOUGHT_DURING_CONVERSATION = 'SUICIDAL_THOUGHT_DURING_CONVERSATION_PAYLOAD'

    GREETING = 'GREETING'
    CCT_1 = "CCT_1"
    CCT_2 = "CCT_2"
    CCT_3 = "CCT_3"
    CCT_4 = "CCT_4"
    CCT_5 = "CCT_5"

    SESSION_1 = "SESSION_1"
    SESSION_2 = "SESSION_2"

    ASK_SUICIDE_ILLNESS = "ASK_SUICIDE_ILLNESS"
    HAVE_SUICIDE_ILLNESS = "HAVE_SUICIDE_ILLNESS"

    GET_STARTED = "GET_STARTED_PAYLOAD"

    REMIND = 'REMIND_PAYLOAD'

    SESSION_END = 'PAYLOAD_SESSION_END'

    ASK_MOOD_END = "PAYLOAD_ASK_MOOD_END"

    intro_payload_list = [
        GREETING,
        CCT_1,
        CCT_2,
        CCT_3,
        CCT_4,
        CCT_5,
        SESSION_1,
        SESSION_2,
        MESSAGE_WITHOUT_BUTTON_IN_INTRO,
        GET_STARTED,
        ASK_SUICIDE_ILLNESS,
        HAVE_SUICIDE_ILLNESS
    ]
