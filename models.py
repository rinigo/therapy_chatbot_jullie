from datetime import datetime, timedelta
import logging
import requests
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, SmallInteger, String, text, Text, desc, and_, exists, \
    or_
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import os
from sqlalchemy.orm import sessionmaker
from common.constant import intro_position
from common.constant.session_status import SessionStatus
from common.constant.user_status import UserStatus

Base = declarative_base()

try:
    db_url = os.environ.get('DATABASE_URL')
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)
except:
    logging.exception('')


class SessionContext(object):
    def __init__(self, session):
        self.session = session

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.session.flush()
            self.session.commit()
            self.session.close()
        except:
            logging.exception('')
            self.session.close()


class SessionFactory(object):
    @staticmethod
    def create():
        try:
            return SessionContext(DBSession())
        except:
            logging.exception('')


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    sender_id = Column(BigInteger, nullable=False, unique=True)
    first_name = Column(String(255), nullable=False)
    middle_name = Column(String(255), server_default=text("NULL::character varying"))
    last_name = Column(String(255), server_default=text("NULL::character varying"))
    nickname = Column(String(255), server_default=text("NULL::character varying"))
    status = Column(SmallInteger, nullable=False, server_default=text("0"))
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    @classmethod
    def find_by_id(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                user = db_session \
                    .query(
                    cls.sender_id,
                    cls.first_name,
                    cls.status
                ) \
                    .filter(cls.id == user_id).all()[0]

                return user
            except:
                logging.exception('')

    @classmethod
    def find_by_sender_id(cls, sender_id):
        with SessionFactory.create() as db_session:
            try:
                user_id = db_session \
                    .query(cls.id) \
                    .filter(cls.sender_id == sender_id).limit(1).all()[0][0]

                return user_id
            except:
                logging.exception('')

    @classmethod
    def register_user(cls, sender_id):
        with SessionFactory.create() as db_session:
            try:
                user_id = db_session \
                    .query(cls.id) \
                    .filter(cls.sender_id == sender_id).limit(1).all()

                if not user_id:
                    user_profile = cls.__get_user_profile(sender_id)

                    new_user = cls()
                    new_user.sender_id = sender_id
                    new_user.first_name = user_profile['first_name']
                    new_user.last_name = user_profile['last_name']

                    db_session.add(new_user)
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def __get_user_profile(cls, fbid):
        try:
            url = "https://graph.facebook.com/v2.6/" + str(
                fbid) + "?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=" + str(
                os.environ.get("PAGE_ACCESS_TOKEN", None))

            user_profile = requests.get(url).json()

            if user_profile is None:
                user_profile = cls.__get_unknown_profile_information()
            else:
                if 'error' in user_profile.keys():
                    user_profile = cls.__get_unknown_profile_information()

            return user_profile
        except:
            logging.exception('')

    @classmethod
    def __get_unknown_profile_information(cls):
        return {'first_name': 'UNKNOWN_FIRST_NAME', 'last_name': None}

    @classmethod
    def update_status(cls, status, user_id):
        with SessionFactory.create() as db_session:
            try:
                user_to_update = db_session.query(cls).filter(cls.id == user_id).all()[0]
                user_to_update.status = status
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def find_possible_remind_users(cls):
        with SessionFactory.create() as db_session:
            try:
                filter_1 = cls.created_at > datetime(2018, 5, 9)

                filter_2 = ~cls.status.in_(
                    [UserStatus.GET_STARTED.value, UserStatus.INTRO.value, UserStatus.SUICIDE_ILLNESS_INTRO.value,
                     UserStatus.SUICIDE_IN_SESSION.value])

                possible_remind_users = db_session.query(cls.id) \
                    .filter(and_(filter_1, filter_2)).order_by(cls.id).all()

                possible_remind_users = [i[0] for i in possible_remind_users]

                return possible_remind_users
            except:
                logging.exception('')

    @classmethod
    def find_unfinished_message_users(cls):
        with SessionFactory.create() as db_session:
            try:
                interval = 20

                unfinished_message_users = db_session \
                    .query(cls.id) \
                    .filter(
                    exists().where(
                        and_(
                            Message.user_id == cls.id,
                            Message.created_at > datetime.utcnow() - timedelta(seconds=interval)
                        )
                    )
                ).all()

                unfinished_message_users = [i[0] for i in unfinished_message_users]

                return unfinished_message_users
            except:
                logging.exception('')
                return []

    @classmethod
    def find_intro_users(cls, unread_messages):
        with SessionFactory.create() as db_session:
            try:
                intro_users = db_session \
                    .query(cls.id) \
                    .filter(
                    and_(
                        cls.id.in_([i[0] for i in unread_messages]),
                        cls.status.in_([0, 1, 7])
                    )
                ).all()

                if intro_users:
                    intro_users = [i[0] for i in intro_users]

                return intro_users
            except:
                logging.exception('')
                return []

    @classmethod
    def find_inactivated_user_ids(cls):
        with SessionFactory.create() as db_session:
            try:
                inactivated_sessions = db_session \
                    .query(Session.user_id) \
                    .filter(
                    and_(
                        Session.status == SessionStatus.active.value,
                        Session.finish_at < datetime.utcnow() - timedelta(minutes=5),
                        Session.created_at > datetime(year=2018, month=6, day=22)
                    )
                ).distinct(Session.user_id).all()

                if inactivated_sessions:
                    inactivated_user_ids = [i[0] for i in inactivated_sessions]
                else:
                    inactivated_user_ids = []

                print("\nINACTIVATED_USER\n{}".format(inactivated_user_ids))

                return inactivated_user_ids
            except:
                logging.exception('')
                return []

    @classmethod
    def find_sender_id_by_id(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                sender_id = db_session \
                    .query(cls.sender_id) \
                    .filter(cls.id == user_id).limit(1).all()[0][0]

                return sender_id
            except:
                logging.exception('')

    @classmethod
    def find_users_in_worker(cls, finished_messages):
        with SessionFactory.create() as db_session:
            try:
                finished_message_users = [i[0] for i in finished_messages]

                users_in_worker = db_session \
                    .query(cls.id) \
                    .filter(
                    and_(
                        cls.id.in_(finished_message_users),
                        exists().where(
                            and_(
                                Message.user_id == cls.id,
                                Message.read_flag == 1,
                                Message.status == 0,
                                Message.created_at > datetime.utcnow() - timedelta(minutes=3)
                            )
                        )
                    )
                ).all()

                users_in_worker = [i[0] for i in users_in_worker]

                if not users_in_worker:
                    return []
                else:
                    return users_in_worker
            except:
                logging.exception('')
                return []

    @classmethod
    def find_first_name_by_id(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                first_name = db_session \
                    .query(cls.first_name) \
                    .filter(cls.id == user_id).all()[0][0]

                return first_name
            except:
                logging.exception('')


class MessageCluster(Base):
    __tablename__ = 'message_clusters'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    length = Column(String(255), server_default=text("NULL::character varying"))
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship('User')

    @classmethod
    def register_new_message_cluster(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                new_message_cluster = cls()
                new_message_cluster.user_id = user_id

                db_session.add(new_message_cluster)
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def find_id_by_user_id(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                cluster_id = db_session \
                    .query(cls.id) \
                    .filter(cls.user_id == user_id).order_by(desc(cls.id)).limit(1).all()

                cluster_id = cluster_id[0][0]

                return cluster_id
            except:
                logging.exception('')

    @classmethod
    def find_last_2_message_cluster_time(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                last_two_message_cluster_time = db_session \
                    .query(
                    cls.created_at
                ) \
                    .filter(
                    cls.user_id == user_id
                ).order_by(desc(cls.created_at)).limit(2).all()

                last_two_message_cluster_time = [i[0] for i in last_two_message_cluster_time]

                return last_two_message_cluster_time
            except:
                logging.exception('')
                return []


class Reaction(Base):
    __tablename__ = 'reactions'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    reaction_id = Column(SmallInteger, nullable=False, server_default=text("0"))
    reaction_type = Column(String(255), nullable=False, server_default=text("0"))
    status = Column(SmallInteger, nullable=False, server_default=text("0"))
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship('User')

    @classmethod
    def enable_old_reactions(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                reaction_to_update = db_session \
                    .query(cls) \
                    .filter(
                    and_(
                        cls.user_id == user_id,
                        cls.created_at < datetime.utcnow() - timedelta(hours=8)
                    )
                ).all()

                for reaction in reaction_to_update:
                    reaction.status = 1
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def enable_reaction_number(cls, user_id, reaction_type, used_list=None):
        with SessionFactory.create() as db_session:
            try:
                if used_list is None:
                    reaction_to_update = db_session \
                        .query(cls) \
                        .filter(
                        and_(
                            cls.user_id == user_id,
                            cls.reaction_type == reaction_type,
                            cls.status == 0
                        )
                    ).all()
                else:
                    reaction_to_update = db_session \
                        .query(cls) \
                        .filter(
                        and_(
                            cls.user_id == user_id,
                            cls.reaction_id.in_(used_list),
                            cls.status == 0
                        )
                    ).all()

                for reaction in reaction_to_update:
                    reaction.status = 1
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def disable_reaction_number(cls, user_id, reaction_id, reaction_type):
        with SessionFactory.create() as db_session:
            try:
                new_reaction_number = cls()

                new_reaction_number.user_id = user_id
                new_reaction_number.reaction_id = str(reaction_id)
                new_reaction_number.reaction_type = reaction_type

                db_session.add(new_reaction_number)
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def find_used_reaction_number(cls, user_id, reaction_type):
        with SessionFactory.create() as db_session:
            try:
                cls.enable_old_reactions(user_id)

                used_reaction_number = db_session \
                    .query(cls.reaction_id) \
                    .filter(
                    and_(
                        cls.user_id == user_id,
                        cls.reaction_type == reaction_type,
                        cls.status == 0
                    )
                ).all()

                used_reaction_number = [i[0] for i in used_reaction_number]

                return used_reaction_number
            except:
                logging.exception('')
                return []


class Session(Base):
    __tablename__ = 'sessions'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    status = Column(SmallInteger, nullable=False, server_default=text("0"))
    mood_start = Column(String(255), server_default=text("NULL::character varying"))
    mood_end = Column(String(255), server_default=text("NULL::character varying"))
    comment_end = Column(Text, server_default=text("NULL::character varying"))
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    finish_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship('User')

    @classmethod
    def create_prepared_session(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                new_session = cls()
                new_session.user_id = user_id
                new_session.status = SessionStatus.prepared.value

                db_session.add(new_session)
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def find_latest_id_by_user_id(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                user_session = db_session \
                    .query(cls) \
                    .filter(cls.user_id == user_id).order_by(desc(cls.id)).limit(1).all()

                if user_session:
                    return user_session[0].id
                else:
                    return None
            except:
                logging.exception('')

    @classmethod
    def find_latest_session_finish_at(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                latest_session_time = db_session \
                    .query(cls.finish_at) \
                    .filter(cls.user_id == user_id).order_by(desc(cls.id)).limit(1).all()[0][0]

                if latest_session_time:
                    return latest_session_time
                else:
                    return None
            except:
                logging.exception('')

    @classmethod
    def find_latest_session_data(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                user_session = db_session \
                    .query(cls.id, cls.user_id, cls.status, cls.finish_at) \
                    .filter(cls.user_id == user_id).order_by(desc(cls.id)).limit(1).all()

                if user_session:
                    user_session = [i._asdict() for i in user_session][0]
                    return user_session
                else:
                    return None
            except:
                logging.exception('')

    @classmethod
    def update_status(cls, session_id, status):
        with SessionFactory.create() as db_session:
            try:
                session_to_update = db_session \
                    .query(cls) \
                    .filter(cls.id == session_id).limit(1).all()[0]

                session_to_update.status = status
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def update_finish_at(cls, session_id, finish_at):
        with SessionFactory.create() as db_session:
            try:
                session_to_update = db_session \
                    .query(cls) \
                    .filter(cls.id == session_id).limit(1).all()[0]

                session_to_update.finish_at = finish_at
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def update_latest_session_status(cls, session_status: SessionStatus, user_id):
        with SessionFactory.create() as db_session:
            try:
                session_to_update = db_session \
                    .query(cls) \
                    .filter(cls.user_id == user_id).order_by(desc(cls.id)).limit(1).all()[0]

                if session_to_update:
                    session_to_update.status = session_status
            except:
                logging.exception('')

    @classmethod
    def save_comment_end(cls, session_id, message):
        with SessionFactory.create() as db_session:
            try:
                comment = ''.join([i['text'] for i in message.message_dicts])

                session_to_update = db_session \
                    .query(cls) \
                    .filter(
                    cls.id == session_id
                ).all()[0]

                print('\n[SAVING COMMENT]')

                session_to_update.comment_end = comment
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def save_mood_end(cls, user_id, mood: str):
        with SessionFactory.create() as db_session:
            try:
                session_to_update = db_session \
                    .query(cls) \
                    .filter(cls.user_id == user_id).order_by(desc(cls.id)).limit(1).all()[0]

                print('\n[SAVING MOOD]')

                session_to_update.mood_end = mood
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def update_existing_sessions(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                existing_sessions = db_session \
                    .query(cls) \
                    .filter(cls.user_id == user_id).all()

                for sess in existing_sessions:
                    sess.finish_at = datetime.utcnow() - timedelta(hours=9)
                    sess.status = SessionStatus.ended.value
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def create_new_session(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                new_session = cls()
                new_session.user_id = user_id
                new_session.finish_at = datetime.utcnow() + timedelta(minutes=30)

                db_session.add(new_session)
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def admin_create_asking_comment_session(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                new_session = cls()
                new_session.user_id = user_id
                new_session.status = SessionStatus.asking_comment.value
                new_session.finish_at = datetime.utcnow() - timedelta(minutes=35)

                db_session.add(new_session)
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def admin_update_status_asking_comment(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                sessions = db_session \
                    .query(cls) \
                    .filter(cls.user_id == user_id).order_by(desc(cls.id)).all()

                for idx, i in enumerate(sessions):
                    i.finish_at = datetime.utcnow() - timedelta(minutes=35)
                    if idx == 0:
                        i.status = SessionStatus.asking_comment.value
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def fetch_session_started_time(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                session_started_time = db_session \
                    .query(
                    Session.created_at
                ).filter(
                    Session.user_id == user_id,
                ).order_by(Session.created_at.desc()).all()[0][0]

                return session_started_time
            except:
                logging.exception('')
                return ""

    @staticmethod
    def fetch_session_ended_time(user_id):
        with SessionFactory.create() as db_session:
            try:
                session_ended_time = db_session \
                    .query(
                    Session.finish_at
                ).filter(
                    Session.user_id == user_id,
                ).order_by(Session.created_at.desc()).all()[0][0]

                return session_ended_time

            except:
                logging.exception('')
                return ""


class Message(Base):
    __tablename__ = 'messages'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    session_id = Column(ForeignKey('sessions.id'), nullable=True)
    cluster_id = Column(ForeignKey('message_clusters.id'))
    message = Column(Text, nullable=False)
    status = Column(SmallInteger, nullable=False, server_default=text("0"))
    read_flag = Column(SmallInteger, nullable=False, server_default=text("0"))
    payload = Column(String(255), server_default=text("NULL::character varying"))
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    cluster = relationship('MessageCluster')
    user = relationship('User')
    db_session = relationship('Session')

    @classmethod
    def find_unread_messages(cls):
        with SessionFactory.create() as db_session:
            try:
                unread_messages = db_session \
                    .query(
                    cls.user_id,
                    cls.message,
                    cls.id
                ) \
                    .filter(
                    and_(
                        cls.read_flag == 0,
                        cls.status == 0
                    )
                ) \
                    .order_by(cls.user_id).all()

                return unread_messages
            except:
                logging.exception('')
                return []

    @classmethod
    def find_cluster_id(cls, message_dict):
        with SessionFactory.create() as db_session:
            try:
                message_id_list = [i['id'] for i in message_dict]

                cluster_id = db_session \
                    .query(
                    cls.cluster_id
                ) \
                    .filter(
                    cls.id.in_(message_id_list)
                ).limit(1).all()

                if cluster_id:
                    return cluster_id[0][0]
                else:
                    return None
            except:
                logging.exception('')

    @classmethod
    def find_latest_message_time(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                latest_message_time = db_session \
                    .query(
                    cls.created_at
                ) \
                    .filter(
                    cls.user_id == user_id
                ).order_by(desc(cls.id)).limit(1).all()

                if not latest_message_time:
                    return None
                else:
                    latest_message_time = latest_message_time[0][0]

                return latest_message_time
            except:
                logging.exception('')

    @classmethod
    def tag_msg_by_session_id(cls, session_id, message_id_list):
        with SessionFactory.create() as db_session:
            try:
                messages_to_update = db_session \
                    .query(cls) \
                    .filter(
                    cls.id.in_(message_id_list)
                ).all()

                for m in messages_to_update:
                    m.session_id = session_id
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def change_current_and_new_message_status(cls, message_id_list, user_id):
        with SessionFactory.create() as db_session:
            try:
                message_to_update = db_session \
                    .query(cls) \
                    .filter(
                    and_(
                        cls.id >= message_id_list[0],
                        cls.user_id == user_id
                    )
                ).all()

                for m in message_to_update:
                    m.read_flag = 0
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def has_user_sent_new_message(cls, user_id, message_id_list):
        with SessionFactory.create() as db_session:
            try:
                new_message = db_session \
                    .query(cls) \
                    .filter(
                    and_(
                        cls.user_id == user_id,
                        cls.id > max(message_id_list)
                    )
                ).all()

                if new_message:
                    return True
                else:
                    return False
            except:
                logging.exception('')
                return False

    @classmethod
    def find_second_last_message_time(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                second_last_message_time = db_session \
                    .query(
                    cls.created_at
                ) \
                    .filter(
                    and_(
                        cls.user_id == user_id,
                        cls.read_flag == 1
                    )
                ).order_by(desc(cls.id)).limit(2).all()

                return second_last_message_time[1][0]
            except:
                logging.exception('')
                return []

    @classmethod
    def update_read_flag(cls, status, message_id):
        with SessionFactory.create() as db_session:
            try:
                message_to_update = db_session \
                    .query(cls) \
                    .filter(cls.id == message_id).first()

                message_to_update.read_flag = status
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def handle_failed_messages(cls):
        # return a list like [[user_id, message_text, message_id], [1, 'hoge', 34]]
        with SessionFactory.create() as db_session:
            try:
                failed_messages = db_session \
                    .query(cls) \
                    .filter(
                    and_(
                        cls.status == 0,
                        cls.read_flag == 1,
                        cls.created_at < datetime.utcnow() - timedelta(minutes=10)
                    )
                ).order_by(cls.id).all()

                if not failed_messages:
                    return

                failed_message_users = list(set([i.id for i in failed_messages]))
                messages_to_unread = []
                messages_to_read = []
                for i in failed_message_users:
                    newest_successful_message_id = db_session \
                        .query(cls.id) \
                        .filter(
                        and_(
                            cls.user_id == i,
                            cls.status == 1
                        )
                    ).order_by(desc(cls.id)).limit(1).all()

                    this_user_messages = [i for i in failed_messages if i.id == i]
                    if any(i.id < newest_successful_message_id for i in this_user_messages):
                        messages_to_read.extend(this_user_messages)
                    else:
                        messages_to_unread.extend(this_user_messages)

                for i in messages_to_unread:
                    i.read_flag = 0

                for i in messages_to_read:
                    i.status = 1
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def change_message_status(cls, message_id_list):
        with SessionFactory.create() as db_session:
            try:
                message_to_update = db_session \
                    .query(
                    cls
                ) \
                    .filter(
                    and_(
                        cls.id.in_(message_id_list),
                        cls.status == 0
                    )
                ).all()

                for message in message_to_update:
                    message.status = 1
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def save_message(cls, user_id, created_at, message, payload=''):
        with SessionFactory.create() as db_session:
            try:
                new_message = cls()
                new_message.user_id = user_id
                new_message.message = message
                new_message.created_at = created_at
                new_message.payload = payload

                db_session.add(new_message)
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def tag_messages_with_cluster_id(cls, message_id_list, cluster_id):
        with SessionFactory.create() as db_session:
            try:
                message_to_update = db_session \
                    .query(cls) \
                    .filter(
                    cls.id.in_(message_id_list)
                ).all()

                for message in message_to_update:
                    message.cluster_id = cluster_id
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def fetch_previous_msg(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                latest_cluster_id = db_session \
                    .query(
                    Message.cluster_id
                ) \
                    .filter(
                    Message.user_id == user_id
                ) \
                    .order_by(
                    desc(Message.created_at)).limit(1).all()[0][0]

                if latest_cluster_id is None:
                    return ""

                previous_msg_list = db_session \
                    .query(
                    Message.message
                ) \
                    .filter(
                    Message.user_id == user_id,
                    Message.cluster_id == latest_cluster_id - 1
                ) \
                    .all()[0]

                if len(previous_msg_list) == 0 or previous_msg_list is None:
                    return ""

                else:
                    return previous_msg_list[0]

            except:
                logging.exception('')
                return ""

    @classmethod
    def count_total_msg_in_session(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                session_started_time = Session.fetch_session_started_time(user_id)
                session_ended_time = Session.fetch_session_ended_time(user_id)
                total_number_of_msg_in_session = db_session \
                    .query(
                    Message
                ) \
                    .filter(
                    Message.user_id == user_id,
                    Message.created_at > session_started_time,
                    Message.created_at < session_ended_time
                ).count()

                return total_number_of_msg_in_session


            except:
                logging.exception('')
                return ""


class Response(Base):
    __tablename__ = 'responses'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    cluster_id = Column(ForeignKey('message_clusters.id'))
    type = Column(String(255), nullable=False)
    response = Column(Text, nullable=False)
    sent_at = Column(DateTime, nullable=False)
    sent_flag = Column(SmallInteger, nullable=False, server_default=text("0"))
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    cluster = relationship('MessageCluster')
    user = relationship('User')

    @classmethod
    def save_response_data(cls, user_id, cluster_id, response, message_types: list, delay=0, has_sent=False):
        with SessionFactory.create() as db_session:
            try:
                new_response = cls()
                new_response.user_id = user_id
                new_response.cluster_id = cluster_id
                new_response.response = response
                new_response.type = ' '.join(message_types)

                if has_sent:
                    new_response.sent_at = datetime.utcnow()
                    new_response.sent_flag = 1
                else:
                    new_response.sent_at = datetime.utcnow() + timedelta(seconds=delay)
                    new_response.sent_flag = 0

                db_session.add(new_response)
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def exists_future_message(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                response_id = db_session \
                    .query(cls.id) \
                    .filter(
                    and_(
                        cls.user_id == user_id,
                        cls.sent_flag == 0
                    )
                ).order_by(cls.sent_at).limit(1).all()

                if response_id:
                    return True
                else:
                    return False
            except:
                logging.exception('')
                return False

    @classmethod
    def find_unsent_message_data(cls):
        with SessionFactory.create() as db_session:
            try:
                unsent_messages = db_session \
                    .query(
                    cls.id,
                    cls.user_id,
                    cls.response
                ) \
                    .filter(
                    and_(
                        cls.sent_at < datetime.utcnow(),
                        cls.sent_flag == 0
                    )
                ).order_by(cls.id).all()

                return unsent_messages
            except:
                logging.exception('')
                return []

    @classmethod
    def update_response_sent_flag(cls, unsent_messages):
        with SessionFactory.create() as db_session:
            try:
                response_id_list = [i[0] for i in unsent_messages]

                response_to_update = db_session \
                    .query(cls) \
                    .filter(
                    and_(
                        cls.sent_flag == 0,
                        or_(
                            cls.id.in_(response_id_list),
                            cls.sent_at < datetime.utcnow() - timedelta(minutes=10),
                            cls.sent_at > datetime.utcnow() + timedelta(minutes=10)
                        )
                    )
                ).all()

                for response in response_to_update:
                    response.sent_flag = 1
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def find_past_3_response_types(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                last_3_cluster_ids = db_session \
                    .query(MessageCluster.id) \
                    .filter(MessageCluster.user_id == user_id).order_by(desc(MessageCluster.id)).limit(3).all()

                last_3_cluster_ids = [i[0] for i in last_3_cluster_ids]

                past_response_types = db_session \
                    .query(
                    cls.cluster_id,
                    cls.type
                ) \
                    .filter(cls.cluster_id.in_(last_3_cluster_ids)).order_by(cls.cluster_id).all()

                if past_response_types:
                    response_types = []
                    for cluster_id in last_3_cluster_ids:
                        r_types = [i[1].split(' ') for i in past_response_types if i[0] == cluster_id]

                        if r_types:
                            response_types += r_types[0]

                    return response_types
                else:
                    return []
            except:
                logging.exception('')
                return []

    @classmethod
    def fetch_last_response_type_list(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                last_response_types = db_session \
                    .query(
                    Response.type
                ) \
                    .filter(
                    Response.user_id == user_id
                ).order_by(desc(Response.created_at)).limit(3).all()[0][0].split()

                return last_response_types
            except:
                logging.exception('')
                return []

    @classmethod
    def fetch_all_response_type_during(cls, session_started_time, session_ended_time, user_id):
        with SessionFactory.create() as db_session:
            try:
                past_response_types = db_session \
                    .query(
                    Response.cluster_id,
                    Response.type
                ) \
                    .filter(
                    Response.user_id == user_id,
                    Response.created_at > session_started_time,
                    Response.created_at < session_ended_time
                ).all()

                return past_response_types
            except:
                logging.exception('')
                return []

    @classmethod
    def fetch_previous_msg_response_type(cls, user_id):
        # TODO see the previous response type and return correct response type
        with SessionFactory.create() as db_session:
            try:
                previous__msg_response_type_list = db_session \
                    .query(
                    Response.type
                ) \
                    .filter(
                    Response.user_id == user_id
                ) \
                    .order_by(desc(Response.id)).limit(1).all()[0]

                if len(previous__msg_response_type_list) == 0 or previous__msg_response_type_list is None:
                    return []
                else:
                    return previous__msg_response_type_list[0].split()


            except:
                logging.exception('')
                return []


class Remind(Base):
    __tablename__ = 'reminds'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    type = Column(SmallInteger, nullable=False, server_default=text("0"))
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship('User')

    @classmethod
    def register_remind(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                new_remind = cls()
                new_remind.user_id = user_id

                db_session.add(new_remind)
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def find_latest_remind_time(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                latest_remind_time = db_session \
                    .query(
                    cls.created_at
                ) \
                    .filter(
                    cls.user_id == user_id
                ).order_by(desc(cls.id)).limit(1).all()

                if latest_remind_time:
                    return latest_remind_time[0]
                else:
                    return None
            except:
                logging.exception('')

    @classmethod
    def find_reminds_by_created_at(cls, user_id, time):
        with SessionFactory.create() as db_session:
            try:
                # TODO can't pass remind class. find remind here
                remind = db_session \
                    .query(cls) \
                    .filter(
                    and_(
                        cls.user_id == user_id,
                        cls.created_at > time
                    )
                ).order_by(desc(cls.id)).all()

                return remind
            except:
                logging.exception('')

    @classmethod
    def register_remind_mood(cls, mood: str, user_id):
        # TODO can't pass remind class. find remind here
        with SessionFactory.create() as db_session:
            try:
                latest_remind = db_session \
                    .query(cls) \
                    .filter(cls.user_id == user_id).order_by(desc(cls.id)).limit(1).all()[0]

                latest_remind.type = mood
            except:
                db_session.rollback()
                logging.exception('')


class UsersFeeling(Base):
    __tablename__ = 'users_feelings'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    keyword = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship('User')

    @classmethod
    def save_feelings(cls, text_kw_df, user_id):
        with SessionFactory.create() as db_session:
            try:
                if text_kw_df is None:
                    return []

                negative_feeling_df = text_kw_df[text_kw_df.fact.isin([False]) & (text_kw_df.sscore < 0)]

                if negative_feeling_df.empty:
                    return

                for idx, row in negative_feeling_df.iterrows():
                    new_feeling = cls()
                    new_feeling.user_id = user_id
                    new_feeling.keyword = row.word

                    db_session.add(new_feeling)
            except:
                logging.exception('')


class IntroPosition(Base):
    __tablename__ = 'intro_positions'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    position = Column(String(255), nullable=False, server_default=text("0"))
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    finished_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship('User')

    @classmethod
    def register_new_intro(cls, user):
        with SessionFactory.create() as db_session:
            try:
                new_intro_position = cls()
                new_intro_position.user_id = user.id
                new_intro_position.position = intro_position.IntroPosition.GREETING.value

                db_session.add(new_intro_position)
            except:
                db_session.rollback()
                logging.exception('')

    @classmethod
    def find_position_by_user_id(cls, user_id):
        with SessionFactory.create() as db_session:
            try:
                position = db_session \
                    .query(cls.position) \
                    .filter(cls.user_id == user_id).limit(1).all()

                position = position[0][0]

                return position
            except:
                logging.exception('')

    @classmethod
    def save_position(cls, position, user_id):
        with SessionFactory.create() as db_session:
            try:
                position_to_update = db_session \
                    .query(cls) \
                    .filter(cls.user_id == user_id).first()

                position_to_update.position = position
            except:
                db_session.rollback()
                logging.exception('')


# metadata.create_all()


def delete_user_from_table(user_id, table):
    with SessionFactory.create() as db_session:
        try:
            if table == User:
                db_session.query(table).filter(table.id == user_id).delete()
            else:
                db_session.query(table).filter(table.user_id == user_id).delete()
        except:
            db_session.rollback()
            logging.exception('')
