import logging
from typing import List

import models
from common.util.util import send_typing_off, send_typing_on, send_message


class MyDB(object):
    @classmethod
    def control_typing_indicator(cls, user_ids_list):
        try:
            for ids in user_ids_list:
                if not models.Response.exists_future_message(ids[0]):
                    send_typing_off(ids[1])
        except:
            logging.exception('')

    @classmethod
    def send_responses(cls, contents: List[str], cluster_id, sender_id, user_id, response_type,
                       should_send_responses_at_once=False):
        if should_send_responses_at_once:
            cls.__send_responses_at_once(contents, sender_id, user_id, cluster_id, response_type)
        else:
            cls.__send_responses_with_delay(contents, sender_id, user_id, cluster_id, response_type)

        send_typing_off(sender_id)

        return

    @classmethod
    def __send_responses_at_once(cls, contents, sender_id, user_id, cluster_id, message_type: list):
        for content in contents:
            send_message(sender_id, content)
            models.Response.save_response_data(user_id, cluster_id, content, message_type, has_sent=True)

    @classmethod
    def __send_responses_with_delay(cls, contents, sender_id, user_id, cluster_id, response_type):
        try:
            delay = 0

            for idx, content in enumerate(contents):
                try:
                    if idx == 0:
                        send_message(sender_id, content)
                        models.Response.save_response_data(user_id, cluster_id, content, response_type, has_sent=True)
                    else:
                        delay = cls.__update_delay(delay, len(content))
                        models.Response.save_response_data(user_id, cluster_id, content, response_type, has_sent=False,
                                                           delay=delay)

                    send_typing_on(sender_id)
                except:
                    logging.exception('')
        except:
            logging.exception('')

    @staticmethod
    def __update_delay(delay, message_length):
        try:
            if message_length <= 17:
                delay_to_add = 2
            elif 18 <= message_length <= 44:
                delay_to_add = 3
            elif 45 <= message_length <= 64:
                delay_to_add = 4
            elif 65 <= message_length:
                delay_to_add = 5
            else:
                delay_to_add = 0

            delay += delay_to_add

            return delay
        except:
            logging.exception('')
            return 3
