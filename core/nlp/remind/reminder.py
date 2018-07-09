import logging
from datetime import datetime, timedelta
import models
from common.constant.session_status import SessionStatus
from common.constant.string_constant import StringConstant
from common.constant.user_status import UserStatus
from common.util.util import send_quick_replies
from core.models.user import User
from db.my_db import MyDB


class Reminder:
    @classmethod
    def make_remind(cls):
        try:
            remind_users = cls.__fetch_remind_users()
            print("\n[REMIND] users\n{}".format(remind_users))

            cls.__send_remind(remind_users)
        except:
            logging.exception('')

    @classmethod
    def __fetch_remind_users(cls):
        try:
            possible_remind_users = models.User.find_possible_remind_users()

            daily_remind_users = cls.__fetch_remind_users_of_this_time(possible_remind_users)

            return daily_remind_users
        except:
            logging.exception('')

    @classmethod
    def __fetch_remind_users_of_this_time(cls, possible_remind_users):
        try:
            remind_user_id_list = []

            for user_id in possible_remind_users:
                latest_message_time = models.Message.find_latest_message_time(user_id)

                if not latest_message_time:
                    continue

                present_time = datetime.utcnow()
                if cls.__was_last_message_around_now(latest_message_time, present_time):
                    latest_session_end_time = models.Session.find_latest_session_finish_at(user_id)

                    if not cls.__has_passed_more_than_24h(latest_session_end_time):
                        continue

                    latest_remind_time = models.Remind.find_latest_remind_time(user_id)
                    if not latest_remind_time:
                        remind_user_id_list.append(user_id)
                        continue
                    else:
                        if not cls.__has_passed_more_than_24h(latest_remind_time):
                            continue

                    reminds_after_session = models.Remind.find_reminds_by_created_at(user_id, latest_session_end_time)
                    if not reminds_after_session:
                        remind_user_id_list.append(user_id)
                    else:
                        if reminds_after_session[0].created_at > datetime.utcnow() - timedelta(hours=23):
                            continue

                        if len(reminds_after_session) < 3:
                            remind_user_id_list.append(user_id)
                        else:
                            days_passed = present_time.day - latest_session_end_time.day
                            if days_passed % 7 == 0:
                                remind_user_id_list.append(user_id)

            return remind_user_id_list
        except:
            logging.exception('')

    @classmethod
    def __send_remind(cls, remind_users):
        try:
            for user_id in remind_users:
                user = User(user_id)
                MyDB.send_responses(StringConstant.remind_text.value, None, user.sender_id, user_id, ['REMIND'])
                send_quick_replies(user.sender_id, StringConstant.remind_quick_replies_title.value,
                                   StringConstant.remind_quick_replies.value, "REMIND_ASK_MOOD")

                latest_session_id = models.Session.find_latest_id_by_user_id(user_id)
                models.Session.update_status(latest_session_id, SessionStatus.ended.value)

                models.Remind.register_remind(user_id)
        except:
            logging.exception('')

    @classmethod
    def __was_last_message_around_now(cls, latest_message_time, present_time):
        try:
            start = present_time - timedelta(minutes=30)
            end = present_time

            start_value = start.hour * 100 + start.minute
            latest_message_value = latest_message_time.hour * 100 + latest_message_time.minute
            end_value = end.hour * 100 + end.minute

            return start_value < latest_message_value < end_value
        except:
            logging.exception('')

    @classmethod
    def __has_passed_more_than_24h(cls, time):
        try:
            return time < datetime.utcnow() - timedelta(hours=23)
        except:
            logging.exception('')
            return False
