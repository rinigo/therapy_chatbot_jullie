import logging
from datetime import datetime
from sqlalchemy import and_
import models
from common.constant.user_status import UserStatus
from scripts.delete_user_from_db import initialize_database
import sys
import os

if '__name__' == '__main__':
    print('------------------')
    path = os.path.join(os.path.dirname(__file__), '../')
    sys.path.append("Users/yuya.t/jullie/scripts")


class AdminConversationNavigator:
    def __init__(self):
        self.session = initialize_database('production')

    def show_conversation(self):
        try:
            users = self.get_users()

            [print(idx, user.id, user.first_name) for idx, user in enumerate(users)]

            user_selection = input(
                "\n ===Tell me user_id: \n120(a specific user), \n'2:'(see all from 3rd user of the list) \nor just press enter to see all")

            if user_selection:
                if user_selection[-2] == ':':
                    user_selection = int(user_selection[1:-2])
                    users = users[user_selection:]
                else:
                    users = [i for i in users if i.id == i]

            for idx, user in enumerate(users):
                print('\n***********************************\n', idx, 'of', str(len(users)), '\n', 'user_id\n', user.id,
                      '\n ', user.first_name, '\n')

                cluster_ids = self.session \
                    .query(
                    models.MessageCluster.id
                ) \
                    .filter(
                    models.MessageCluster.user_id == user.id
                ).order_by(models.MessageCluster.id).all()

                for cluster_id in cluster_ids:
                    messages = self.session \
                        .query(
                        models.Message.message
                    ) \
                        .filter(
                        models.Message.cluster_id == cluster_id
                    ).order_by(models.Message.id).all()
                    messages = [i[0] for i in messages]

                    responses = self.session \
                        .query(
                        models.Response.response
                    ) \
                        .filter(
                        models.Response.cluster_id == cluster_id
                    ).order_by(models.Response.id).all()
                    responses = [i[0] for i in responses]

                    [print(' - ' + i) for i in messages]
                    print('*')
                    [print('     - ' + i) for i in responses]
                    print('----------------------')

                input("\n=== press enter to see next user")

            print("You saw all the conversations!")
        except:
            logging.exception('')
        finally:
            self.session.close()

    def get_users(self):
        try:
            time = input('=== month day hour in jst (mmddhh)')
            month = int(time[:2])
            day = int(time[2:4])
            hour = int(time[4:]) - 9 if int(time[4:]) >= 9 else 0

            print(month, day, hour)
            users = self.session \
                .query(
                models.User
            ) \
                .filter(
                and_(
                    models.User.created_at > datetime(year=2018, month=month, day=day, hour=hour),
                    ~models.User.status.in_({UserStatus.GET_STARTED.value, UserStatus.INTRO.value,
                                             UserStatus.SUICIDE_ILLNESS_INTRO.value})
                )
            ).order_by(models.User.created_at).all()

            return users
        except:
            logging.exception('')
            return []
