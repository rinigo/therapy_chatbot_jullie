from datetime import datetime, timedelta
import logging
import models
from common.constant.admin_command import AdminCommand
from common.constant.message_type import MessageType
from core.models.user import User
from core.nlp.response_generator.factory.cct_response_generator_factory import CCTResponseGeneratorFactory
from scripts.delete_user_from_db import initialize_database, delete_all_rows_of_a_user


class AdminSendMessage:
    def __init__(self):
        self.env_type = input("Select env type {terada, miyamoto, master, production}")
        self.test_type = input("select test type.\n if you want to test regular conversation, press enter. \nIf not, type something")
        self.db_sess = initialize_database(self.env_type)
        self.user = User(self.select_user_id())
        self.db_sess_start_time = datetime.utcnow()
        self.th_sess_start_time = datetime.utcnow()

        if not self.test_type:
            self.restart_session()


    def admin_send_message(self, message):
        try:
            if self.db_sess_start_time < datetime.utcnow() - timedelta(minutes=2):
                self.db_sess.close()
                self.db_sess = initialize_database(self.env_type)
                self.db_sess_start_time = datetime.utcnow()

            if not self.test_type:
                if self.th_sess_start_time < datetime.utcnow() - timedelta(minutes=28):
                    self.restart_session()

            new_message = models.Message()
            new_message.message = message
            new_message.user_id = self.user.id
            new_message.created_at = datetime.utcnow() - timedelta(seconds=20)

            self.db_sess.add(new_message)
            self.db_sess.commit()
        except:
            self.db_sess.rollback()
            logging.exception('')

    def select_user_id(self):
        try:
            users = self.db_sess \
                .query(
                models.User
            ) \
                .filter(
                models.User.first_name.in_(['Yuya', 'Rintaro'])
            ).all()

            [print(u.id, u.first_name) for u in users]

            return input('select user_id you use')
        except:
            logging.exception('')

    def admin_go_to_ask_mood(self):
        self.admin_send_message(AdminCommand.GO_TO_ASK_MOOD.value)

    def admin_restart_introduction(self):
        delete_all_rows_of_a_user(self.user.id)

    def restart_session(self):
        admin_response_generator = CCTResponseGeneratorFactory.create(self.user, None, MessageType.ADMIN.value)
        admin_response_generator.restart_session()
        self.th_sess_start_time = datetime.utcnow()

    def __del__(self):
        self.db_sess.close()
