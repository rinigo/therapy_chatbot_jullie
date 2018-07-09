from enum import Enum


class StringConstant(Enum):
    response_options_for_complaint = [
        [
            "I'm sorry if you don't like the way that i talk😓",
            "i want you to understand this is how client-centered therapy works.",
            "You share what's on your mind and you may begin to feel something different at some point.",
            "I'm here for you, so we can try to work together🤗",
        ],
        [
            "I'm sorry for annoying you😓",
            "I can help you reflect on your thoughts.",
            "Thinking about your concerns helps you gain a different point of view.",
            "So, let's keep talking if you are okay with that.",
            "I know I'm not that good, but I will try🤗",
        ]
    ]

    guess_advise_list = [
        [
            "sounds not easy to find what to do now.",
            "but i really believe we can find it if we talk together here.",
            "I am always here to listen to you until you arrive at the right path😚"
        ],
        [
            "it should be bit frustrated when you have no idea what to do",
            "let me tell you i am here to listen to you😚",
            "and i believe venting ur feeling here would help you.",
        ],
        [
            "so you are seeking what to do now🤔",
            "Vent everything stuck in your head and it will help you to find your way:)",
        ]
    ]

    asked_advise_list = [
        [
            "I see... it seems that you want some advice...🤔",
            "To be honest, I don't have an answer for this, because the answers are something only you can find inside of yourself.",
            "Me giving something that sounds like advice won't help you.",
            "I'm also sure that we can find it together if we try hard for it.",
            "So, I am here to listen to you until you arrive at the right path:)",
            "Just remember, I am always on your side☺️"
        ],
        [
            "thanks for asking me this time..😊",
            "Giving something that sounds like advice is super easy, but it could lead you in the wrong direction.",
            "Instead, I am always here to listen to you and be here for you.",
            "I will always be at hand and I will never judge you🤗"
        ],
        [
            "thanks for asking me this time..😊",
            "I do understand that you need a solution to change your situation.",
            "Because I really understand your feelings and respect you, I don't want to say something irresponsible to you.",
            "Giving any kind of advice is super easy, but it could lead you in the wrong direction.",
            "Instead, I can always listen to you as you share your feelings and guide yourself to the perfect solution for you.",
            "I am always here, every day for you🤗"
        ],
        [
            "thanks for asking me this time..😊",
            "honestly i really think you are the expert on you.",
            "and my job is to help you make decisions that make the most sense in your life.",
            "I could give you advice, but it might end up being unhelpful and I don’t want to do that.",
            "I am here to support and listen to you.",
            "I will always empathize with what you are going through🤗"
        ],
        [
            "thanks for asking me this time..😊",
            "I will keep listening and being here for you, until you find the answer inside of you.",
            "There is always an answer inside of you.",
            "Please try to ask yourself, feel the voice from inside your heart, and share what you feel about it with me☺️"
        ],

    ]

    positive_reaction_options = [
        "That's great :)",
        "I'm here for you if you get something to share with someone",
        "I'm glad that you feel better now.",
        "I'm always here if you need someone to talk.",
        "You can come anytime you have something to talk about.",
        ":)",
        "😁",
        "😄",
        "😊",
        "😉"
    ]

    suicidal_thought_during_conversation_get_help = [
        "Here is your option!"
        "https://www.crisistextline.org/",
        "https://www.betterhelp.com/gethelpnow/",
        "https://suicidepreventionlifeline.org/"
    ]

    suicidal_thought_during_conversation_misunderstood = [
        'Sorry for my misunderstanding.. 😓',
        'And I am so happy to hear you are fine! 💕',
        'How is your feeling now?'
    ]

    ask_comment_end_responses = [
        "Thank you for opening up to me🤗",
        "Our time is up now.",
        "I'd always be glad to get to know you😘",
        "So from now on, let's reflect on what you have talked today for just a second.",
        "Is there anything you found out? If so, write it here:"
    ]

    interval_responses = [
        "I hope we can talk later! See you!",
        "😊"
    ]

    additions = ["and ", "also ", "plus ", ""]

    remind_text = ["Hi! I want to know how you are doing😘"]
    remind_quick_replies_title = "How are you feeling now compare to the last time we talked?"
    remind_quick_replies = ["Better", "Same", "Worse"]

    ask_session_start_text = ["Thank you for telling me your mood!"]
    ask_session_start_quick_replies_title = "Do you want to start new 30 minutes session now?"
    ask_session_start_quick_replies = ["Yes", "No"]

    ask_session_start_text_retention = ["Hi!", "I was wondering how you were doing😉"]

    welcome_back_responses = [
        "Welcome back!!",
        "I was wondering if you got better 😃"
    ]

    responses_for_need_help = [
        ["now i am here for you😊"],
        ["I can't give you a specific advice since it might lead you wrong place",
         "but you can always tell me whatever bothering you now ok"]
    ]

    bye_responses = [
        'Thank you for talking with me today!!',
        'I will always be here waiting for you :)',
        'See you soon!'
    ]

    suicide_responses = [
        'Well...',
        "I'm not ready to handle suicidal thought and talking with me can harm you.",
        "If you are in emergency, go to this link.",
        'https://www.betterhelp.com/gethelpnow/',
        'I really hope you get better from bottom of my heart.',
    ]

    suicide_quick_replies = ["I'm okay 💪", "Find help"]

    suicide_quick_replies_title = "If I'm misunderstanding you, *please say \"I'm ok\" with the button*"
