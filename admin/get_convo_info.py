import numpy as np
from scripts.delete_user_from_db import initialize_database
from sqlalchemy import and_, desc, exists
from datetime import datetime, timedelta
import models


def get_convo_info(start_month, start_day, end_month=datetime.utcnow().month, end_day=datetime.utcnow().day):
    """
    this is valid for 6/22-7/3(current date)

    :param start_month:
    :param start_day:
    :param end_month:
    :param end_day:
    :return:
    """
    session = initialize_database('production')

    start_date = datetime(year=2018, month=start_month, day=start_day)
    end_date = datetime(year=2018, month=end_month, day=end_day)

    s1 = ~models.User.first_name.in_(['Yuya', 'Rintaro'])
    s2 = models.User.created_at > start_date
    s3 = models.User.created_at < end_date
    new_users = session.query(models.User).filter(and_(s1, s2, s3)).order_by(desc(models.User.id)).all()
    new_user_ids = [i.id for i in new_users]

    print('\nnew users\n', len(new_users), new_user_ids[-5:])

    new_messages = session.query(models.Message).filter(models.Message.user_id.in_(new_user_ids)).all()

    print("\nnew messages\n", len(new_messages))

    s1 = models.User.status.in_([0, 1])
    s2 = models.User.id.in_(new_user_ids)
    intro_users = session.query(models.User).filter(and_(s1, s2)).all()

    print("\nintro users\n", len(intro_users))

    s1 = exists().where(
        and_(
            models.Session.user_id == models.User.id,
            models.Session.status != 4
        )
    )
    s2 = models.User.id.in_(new_user_ids)
    s3 = models.User.status == 2

    regular_convo_users = session.query(models.User).filter(and_(s1, s2, s3)).all()

    print("\nnew regular convo users\n", len(regular_convo_users))

    regular_convo_user_ids = [i.id for i in regular_convo_users]

    msg_per_user = []
    for i in regular_convo_user_ids:
        s1 = models.Message.user_id == i
        s2 = models.Message.payload == ''
        messages = session.query(models.Message).filter(and_(s1, s2)).all()
        msg_per_user.append(len(messages))

    average_msg_per_user = np.sum(msg_per_user) / len(msg_per_user)
    print('\naverage messages per user\n', average_msg_per_user)

    msg_per_session = []
    for i in regular_convo_user_ids:
        s2 = models.Session.user_id == i
        regular_session = session.query(models.Session).filter(and_(s2)).order_by(models.Session.id).limit(1).all()
        messages = session.query(models.Message).filter(models.Message.session_id == regular_session[0].id).all()
        msg_per_session.append(len(messages))

    avg_msg_per_ssn = np.sum(msg_per_session) / len(msg_per_session)
    print('\naverage messages per session\n', avg_msg_per_ssn)

    returned_users = []
    for i in regular_convo_user_ids:
        s2 = models.Session.user_id == i
        regular_session = session.query(models.Session).filter(and_(s2)).order_by(models.Session.id).limit(2).all()
        if len(regular_session) == 2:
            returned_users.append(i)

    print('\nreturned users\n', returned_users)

    s1 = models.Session.user_id.in_(new_user_ids)
    s2 = models.Session.mood_end != ''
    completed_sessions = session.query(models.Session).filter(and_(s1, s2)).order_by(models.Session.id).all()

    print('\ncompleted sessions\n', len(completed_sessions))
