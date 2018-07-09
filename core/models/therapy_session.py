import logging
from datetime import datetime, timedelta
import models
from common.constant.session_status import SessionStatus


class TherapySession:
    interval_after_session = 8

    def __init__(self, user_id):
        latest_session = models.Session.find_latest_session_data(user_id)

        if latest_session is None:
            self.__id = None
        else:
            self.__id = latest_session['id']
            self.__user_id = latest_session['user_id']
            self.status = latest_session['status']
            self.finish_at = latest_session['finish_at']

    def change_status(self, status: SessionStatus):
        try:
            models.Session.update_status(self.id, status)
            self.status = status
        except:
            logging.exception('')

    def activate(self):
        try:
            self.change_status(SessionStatus.active.value)
            self.update_finish_at()
        except:
            logging.exception('')

    def prepare(self):
        try:
            self.change_status(SessionStatus.prepared.value)
        except:
            logging.exception('')

    def update_finish_at(self):
        try:
            new_finish_at = datetime.utcnow() + timedelta(minutes=30)
            models.Session.update_finish_at(self.id, new_finish_at)
            self.finish_at = new_finish_at
        except:
            logging.exception('')

    @classmethod
    def __finish_remind_questions(cls, user):
        try:
            models.Session.update_latest_session_status(SessionStatus.ended.value, user.id)
        except:
            logging.exception('')

    @property
    def id(self):
        return self.__id

    @property
    def user_id(self):
        return self.__user_id
