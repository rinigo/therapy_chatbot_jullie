import logging
from datetime import timedelta
from pprint import pprint
from rq import Queue
import main
import models
from common.util.util import send_message, send_typing_on
from core.models.user import User
from core.nlp.bot.product.feedback_bot import FeedbackBot
from core.nlp.message_retriever import MessageRetriever
from core.nlp.remind.reminder import Reminder
from db.my_db import MyDB
from worker import conn
from datetime import datetime


def fetch_regularly():
    try:
        message_data = MessageRetriever.fetch_messages_to_process()

        if message_data is None:
            return None
        else:
            try:
                q = Queue('high', connection=conn)

                for data in message_data:
                    q.enqueue(main.main, data)
                    print('\n>>>> Enqueued successfully!\n{}'.format(datetime.utcnow()))
                    pprint(data['user_id'])
                    print("[Remaining jobs in queue]")
                    pprint(q.job_ids)
            except Exception:
                print('Couldn\'t enqueue messages')
                logging.exception('')
    except Exception:
        logging.exception('')


def send_response_regularly():
    try:
        responses = get_unsent_responses()

        if len(responses) == 0:
            return None

        print("\nSending response_generator >>>>>")
        pprint(responses)

        for i in responses:
            send_message(sender_id=i[2], content=i[1])
            send_typing_on(sender_id=i[2])

        user_ids_list = set(map(tuple, [[i[0], i[2]] for i in responses]))

        MyDB.control_typing_indicator(user_ids_list)
    except:
        logging.exception('')


def get_unsent_responses():
    try:
        unsent_messages = models.Response.find_unsent_message_data()
        # e.g. unsent_messages = [(response_id, user_id, response_text),...]

        if len(unsent_messages) == 0:
            return []

        models.Response.update_response_sent_flag(unsent_messages)

        unsent_messages = [list(i) for i in unsent_messages]

        for idx, user_id in enumerate([i[1] for i in unsent_messages]):
            user = User(user_id)

            unsent_messages[idx].append(user.sender_id)

        res_list = [[i[1], i[2], i[3]] for i in unsent_messages]

        return res_list
    except:
        logging.exception('')
        return []


def reminder():
    print('\n[REMIND] start')
    Reminder.make_remind()
    print("\n[REMIND] sent")


def ask_feecback():
    bot = FeedbackBot()

    inactivated_users = bot.find_inactivated_users()

    bot.ask_feed_back(inactivated_users)


if __name__ == '__main__':
    last_remind_time = datetime.utcnow() - timedelta(minutes=30)
    last_feed_back_time = datetime.utcnow() - timedelta(minutes=5)

    while 1 == 1:
        # try:
        #     if datetime.utcnow() > last_remind_time + timedelta(minutes=30):
        #         last_remind_time = datetime.utcnow()
        #         reminder()
        # except:
        #     logging.exception('')

        try:
            if datetime.utcnow() > last_feed_back_time + timedelta(minutes=5):
                last_feed_back_time = datetime.utcnow()
                ask_feecback()
        except:
            logging.exception('')

        try:
            fetch_regularly()
        except:
            logging.exception('')

        try:
            send_response_regularly()
        except:
            logging.exception('')
