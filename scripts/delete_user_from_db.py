import logging
import models
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def initialize_database(env_type):
    database_url = ""

    Base = declarative_base()
    metadata = Base.metadata
    engine = create_engine(database_url)
    metadata.bind = engine

    Session = sessionmaker(bind=engine)
    session = Session()

    return session


def delete_all_rows_of_a_user(user_id, from_messenger=False):
    if from_messenger:
        try:
            tables_to_delete = [models.UsersFeeling, models.Response, models.IntroPosition, models.Remind,
                                models.Reaction, models.Message, models.MessageCluster, models.Session, models.User]

            for table in tables_to_delete:
                print("deleting: {}...".format(table))
                models.delete_user_from_table(user_id, table)

            print('Deleted the user ' + str(user_id))
        except:
            logging.exception('')
    else:
        session = initialize_database(env_type)

        try:
            user = session.query(models.User).filter(models.User.id == user_id).one()
            print(user.id, user.first_name, user.last_name, user.created_at)
        except:
            logging.exception('')
            user = None

        if user is None:
            print('the user of the user_id was not found')
            return

        user_input = input('Do you want to delete this user? y/n')

        if user_input == 'y':
            try:
                tables_to_delete = [models.UsersFeeling, models.Response, models.IntroPosition, models.Remind,
                                    models.Reaction, models.Message, models.MessageCluster, models.Session, models.User]

                for table in tables_to_delete:
                    print("deleting {}...".format(table))
                    models.delete_user_from_table(user_id, table)

                print('Deleted the user ' + str(user_id))
            except:
                logging.exception('')
                print('error deleting the user ' + str(user_id))
                return
        else:
            print('Didnt delete the user ' + str(user_id))
            return user


def search_user(first_name):
    session = initialize_database(env_type)

    try:
        users = session \
            .query(models.User) \
            .filter(models.User.first_name == first_name).order_by(models.User.id).all()

        for user in users:
            print(user.id, user.sender_id, user.status)

        return users
    except:
        logging.exception('')
        print('No user with that first name!')
