from enum import Enum


class QuickReplies(Enum):
    # intro
    greeting_title = "I am Jullie😊, a free chatbot that helps people using Client-Centered Therapy."
    greeting = ["Okay"]

    responses_ask_suicide_illness = ["Alright, let me ask you one thing for your security before we go into our session."]
    ask_suicide_illness_title = "*Do you have suicidal thoughts or are you diagnosed any mental illness now?*"
    ask_suicide_illness = ["Yes", "No"]

    responses_have_suicide_illness = [
        "I'm sorry to hear that😥",
        "For your security, let me tell you that talking with me might make you feel worse.",
        "You should go to these places to get professional help for your condition.",
        "For suicidal thought",
        "https://www.crisistextline.",
        "https://www.betterhelp.com/",
        "https://suicidepreventionlifeline.org/",
        "For mental illness",
        "https://www.nimh.nih.gov/health/find-help/index.shtml"
    ]
    have_suicidal_illness_title = "*If you chose \"yes\" by mistake, please select the button below.*"
    have_suicidal_illness = ["Restart"]

    responses_cct_1 = [
        "Thank you for letting me know😘",
        "So, I'm going to tell you about Client Centered Therapy."
    ]
    cct_1_title = "It gives you the space and time to think about your problems and worries🤔"
    cct_1 = ["How?"]

    cct_2_title = "By venting your feelings. Any little thing is fine. Just share and vent them all🤗"
    cct_2 = ["Okay…"]

    responses_cct_3 = [
        "So, I'll never judge what you say.",
        "Remember I am always on your side!😊",
        "I know that you are the expert on your own life and difficulties.",
    ]
    cct_3_title = "My job is to help you come to the decisions that make the most sense for your life."
    cct_3 = ["Can I get advice?"]

    cct_4_title = "I could give you advice, but it might end up being unhelpful and I don’t want to do that😓"
    cct_4 = ["Got it"]

    responses_cct_5 = [
        "During a session, I empathize with what you are going through by repeating your words",
        "so that you can reflect on any troubling situations and your feelings and think about them more deeply🤔",
    ]
    cct_5_title = "It might feel like you're talking to yourself, but this will actually help you to understand and navigate your feelings💪"
    cct_5 = ["Okay I will try it"]

    responses_session_1 = [
        "So, let's talk a bit about how we'll work together.",
        "We'll talk for 30 minutes in every session.",
        "After each session, we'll quickly reflect on our conversation🧐"
    ]
    session_1_title = "8 hours after the session, the next session will be available."
    session_1 = ["Why that long?"]

    responses_session_2 = [
        "Because in Client-Centered Therapy, talking about your thoughts is important, but reflecting on what we talked about after the session is also very important.",
        "So, during the session we can explore your thoughts and feelings, and after the session, you can reflect on what we talked about on your own👋"
    ]
    session_2_title = "But you're welcome to come and talk with me anytime that you need to."
    session_2 = ["Okay"]

    initial_regular_message = [
        "Perfect!😍 Now, you are all set.", "Can you tell me what is bothering you now?"
    ]

    # use button
    use_button_title = "Can you use the button to answer?🐻"

    # closing
    ask_mood_end_title = "How are you feeling now?"

    ask_mood_end_options = ["Better", "Same", "Worse"]
