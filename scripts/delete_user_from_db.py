import logging
import models
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def initialize_database(env_type):
    database_url = ""
    if env_type == 'terada':
        database_url = "postgres://tabznkdzkmwkxj:47673cdfc5deba088d73b817cd3ec08c47c3de5602bcb18b2f8dd712ad765de0@ec2-54-235-109-37.compute-1.amazonaws.com:5432/dairrpp3kvofa"
    elif env_type == "miyamoto":
        database_url = 'postgres://ukpctvsdiebdan:cea8349eb6fc608282b6da123f02d79a8b5a88b2b8f248dfe8682c75e9be9e4e@ec2-54-221-207-184.compute-1.amazonaws.com:5432/dao5vlq687d8gj'
    elif env_type == 'master':
        database_url = "postgres://fzsfwkqhchaxxj:bb31b882e1b21fabfc24b2ae33de1de9f241d1173c42152cb23e389efd7dce5b@ec2-23-23-248-162.compute-1.amazonaws.com:5432/d9rbv28j387456"
    elif env_type == 'production':
        database_url = "postgres://cejukpqqklshfq:7930f17e10633f0b6f11bb34bf714e65527f7a9e4d6f694bd1c3933b2d03bc01@ec2-54-204-46-60.compute-1.amazonaws.com:5432/danfibvln01sii"

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
        env_type = input("Select env type {terada, miyamoto, master, production}")
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
    env_type = input("Select env type {terada, miyamoto, master, production}")
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
