from enum import Enum


class Intent(Enum):
    NORMAL = 'normal'
    NOT_LISTENING = 'not_listening'
    MEANINGLESS = 'meaningless'
    HATE_REPETITIVE = 'repetitive'
    JULLIE_USELESS = 'jullie_useless'
    COMPLAINT_OR_DISSING = "complaint_or_dissing"
    NO_IDEA = "no_idea"
    NEED_HELP = 'need_help'
    CANT_GET_ATTENTION_FROM_BF = "cant_get_attention_from_bf"
    LACK_OF_CONFIDENCE = "lack_of_confidence"
    QUESTION_NO_IDEA = "NoIdeaQuestionType"
    QUESTION_GENERAL_TYPE = "GeneralQuestionType"
    LIKE_SOMEONE = "like_someone"
    ABOUT_BREAKUP = "about_breakup"
    NO_FRIENDS = "no_friends"
    ANXIOUS = "anxious"
    LONELY = 'lonely'
    CALL_ME_NAMES = 'call_me_names'
    MONEY = 'money'
    LONG_MSGs = "long_msgs"
    MISSING = 'missing'

    YesNoQuestionType = "YesNoQuestionType"
    DoQuestionType = "DoQuestionType"
    BeQuestionType = "BeQuestionType"
    CanQuestionType = "CanQuestionType"
    ShouldQuestionType = "ShouldQuestionType"
    HowQuestionType = "HowQuestionType"
    WhatQuestionType = "WhatQuestionType"
    WhyQuestionType = "WhyQuestionType"
    WouldQuestionType = "WouldQuestionType"
    ForWhatQuestionType = "ForWhatQuestionType"
    WhatIfQuestionType = "WhatIfQuestionType"
    WhatAboutQuestionType = "WhatAboutQuestionType"
    AgreeQuestionType = "AgreeQuestionType"

    PROPER_QUESTION_TYPES = [
        YesNoQuestionType,
        DoQuestionType,
        BeQuestionType,
        CanQuestionType,
        ShouldQuestionType,
        HowQuestionType,
        WhatQuestionType,
        WhyQuestionType,
        WouldQuestionType,
        ForWhatQuestionType,
        WhatIfQuestionType,
        WhatAboutQuestionType,
        AgreeQuestionType
    ]

    UnknownQuestionType = "UnknownQuestionType"
    NoIdeaQuestionType = "NoIdeaQuestionType"

    ALL_QUESTION_TYPES = [
        YesNoQuestionType,
        DoQuestionType,
        BeQuestionType,
        CanQuestionType,
        ShouldQuestionType,
        HowQuestionType,
        WhatQuestionType,
        WhyQuestionType,
        WouldQuestionType,
        ForWhatQuestionType,
        WhatIfQuestionType,
        WhatAboutQuestionType,
        AgreeQuestionType,
        UnknownQuestionType,
        QUESTION_GENERAL_TYPE,
        NoIdeaQuestionType
    ]

    HELLO = 'smalltalk.greetings.hello'
    GOOD_MORNING = 'smalltalk.greetings.goodmorning'
    GOOD_EVENING = 'smalltalk.greetings.goodevening'
    NICE_TO_MEET_YOU = 'smalltalk.greetings.nice_to_meet_you'
    GOOD_NIGHT = 'smalltalk.greetings.goodnight'
    BYE = 'smalltalk.greetings.bye'
    THANK_YOU = 'smalltalk.appraisal.thank_you'
    THERE = 'smalltalk.agent.there'
    SORRY = 'smalltalk.dialog.sorry'

    UNIMPORTANT_1 = [
        HELLO,
        GOOD_MORNING,
        GOOD_EVENING,
        NICE_TO_MEET_YOU,
        GOOD_NIGHT,
        BYE,
        THANK_YOU,
        THERE,
        SORRY
    ]

    NO_PROBLEM = 'smalltalk-.appraisal.no_problem'
    WELCOME = 'smalltalk.appraisal.welcome'
    HAHA = 'haha'
    STICKER = 'sticker'
    CALL_JULLIE = 'call_jullie'

    UNIMPORTANT_2 = [
        NO_PROBLEM,
        WELCOME,
        CALL_JULLIE,
        HAHA,
        STICKER
    ]

    NORMAL_AND_UNIMPORTANT = UNIMPORTANT_1 + UNIMPORTANT_2 + [NORMAL]
    BYE_INTENTS = UNIMPORTANT_1[4:6]

    ALL_UNIMPORTANT = UNIMPORTANT_1 + UNIMPORTANT_2

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)
