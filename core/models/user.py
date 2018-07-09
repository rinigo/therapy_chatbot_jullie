import logging
import models


class User:
    def __init__(self, user_id):
        self.__id = user_id

        user_data = models.User.find_by_id(user_id)
        self.__sender_id = user_data[0]
        self.__first_name = user_data[1]
        self.__status = user_data[2]

    def update_status(self, status):
        try:
            models.User.update_status(status, self.id)
            self.status = status
        except:
            logging.exception('')

    @property
    def id(self):
        return self.__id

    @property
    def sender_id(self):
        return self.__sender_id

    @property
    def first_name(self):
        return self.__first_name

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        try:
            self.__status = status
        except Exception:
            logging.exception('')
