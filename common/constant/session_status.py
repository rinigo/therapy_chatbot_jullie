from enum import Enum


class SessionStatus(Enum):
    # ReturnVisit
    asking_new = 6

    # CCT
    prepared = 4

    # CCT or Reflection
    active = 0

    # Reflection
    asking_comment = 1
    asking_mood = 2
    telling_next_time = 8

    # ReturnVisit will handle all status except prepare 8 hours after last session finish_at

    # Reception or ReturnVisit
    ended = 3

    # Remind
    asking_mood_remind = 5
    asking_new_session_remind = 7
