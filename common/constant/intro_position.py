from enum import Enum


class IntroPosition(Enum):
    GREETING = "GREETING"
    CCT_1 = "CCT_1"
    CCT_2 = "CCT_2"
    CCT_3 = "CCT_3"
    CCT_4 = "CCT_4"
    CCT_5 = "CCT_5"
    SESSION_1 = "SESSION_1"
    SESSION_2 = "SESSION_2"

    ASK_SUICIDE_ILLNESS = "ASK_SUICIDE_ILLNESS"
    HAVE_SUICIDE_ILLNESS = "HAVE_SUICIDE_ILLNESS"

    DONE = "DONE"

    intro_position_list = [GREETING, CCT_1, CCT_2, CCT_3, CCT_4, CCT_5, SESSION_1, SESSION_2, ASK_SUICIDE_ILLNESS,
                           HAVE_SUICIDE_ILLNESS, DONE]
