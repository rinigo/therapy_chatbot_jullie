from enum import Enum


class QuickResponseEmoji(Enum):
    pensive_face = u'\U0001F614'
    pensive_face2 = u'\U0001F614' + u'\U0001F614'
    disappointed_face = u'\U0001F61E'
    disappointed_face2 = u'\U0001F61E' + u'\U0001F61E'
    anxious_face_with_sweat = u'\U0001F630'
    face_without_mouth = u'\U0001F636'
    face_with_rolling_eyes = u'\U0001F644'
    beaming_face_with_smiling_eyes = u'\U0001F601'
    face_blowing_a_kiss = u'\U0001F618'
    smiling_face = u'\U0000263A'
    smiling_face2 = u'\U0000263A' + u'\U0000263A'
    smiling_face_with_smiling_eyes = u'\U0001F60A'
    smiling_cat_face_with_heart_eyes = u'\U0001F63B'
    smiling_cat_face_with_heart_eyes2 = u'\U0001F63B' + u'\U0001F63B'


quick_response_emoji_list = [i.name for i in QuickResponseEmoji]