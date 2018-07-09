import logging
from pprint import pprint
import models


class MessageRetriever:
    @classmethod
    def fetch_messages_to_process(cls):
        try:
            try:
                models.Message.handle_failed_messages()

                unread_messages = models.Message.find_unread_messages()

                intro_users = models.User.find_intro_users(unread_messages)
                intro_user_messages = [i for i in unread_messages if i[0] in intro_users]

                non_intro_user_messages = [i for i in unread_messages if i[0] not in intro_users]

                unfinished_message_users = models.User.find_unfinished_message_users()
                finished_messages = [i for i in non_intro_user_messages if i[0] not in unfinished_message_users]

                users_in_worker = models.User.find_users_in_worker(finished_messages)
                finished_and_not_in_worker_message = [i for i in finished_messages if i[0] not in users_in_worker]

                messages = intro_user_messages + finished_and_not_in_worker_message
            except:
                logging.exception('')
                messages = []

            if not messages:
                return None

            """
            e.g. messages = [
                (1, 'hi',51), 
                (1, 'thank you',53), 
                (2, 'hi',52),
                ...
            ]
            """

            message_data = cls.__format_message_data(messages)

            cls.__change_read_flag(message_data)

            cls.__register_cluster_id(message_data)

            return message_data
        except:
            logging.exception('')

    @staticmethod
    def __format_message_data(messages):
        user_id_list = set([i[0] for i in messages])
        message_data = [{'user_id': i, 'messages': []} for i in user_id_list]

        for m in messages:
            d = {'id': m[2], 'text': m[1]}

            if any(i['user_id'] == m[0] for i in message_data):
                target_dict = [i for i in message_data if i['user_id'] == m[0]][0]
                target_dict_index = message_data.index(target_dict)
                target_dict['messages'].append(d)
                target_dict['messages'] = sorted(target_dict['messages'], key=lambda k: k['id'])
                message_data[target_dict_index] = target_dict
            else:
                message_data.append({'user_id': m[0], 'messages': [d]})
        """
        e.g. message_data =[
            {
                'user_id': 12, 
                'messages': [
                    {'text': hi', 'id': 0}, 
                    {text': 'thank you', 'id': 1}
                ]
            },
            {
            'user_id': 12, 
            'messages': [
                {'text': hi', 'id': 0}, 
                {text': 'thank you', 'id': 1}
                ]
            }
        ] 
        """
        message_data = sorted(message_data, key=lambda k: k['user_id'])
        print('\n*************************\nmessage_data')
        pprint(message_data)

        return message_data

    @staticmethod
    def __change_read_flag(message_data):
        try:
            handled_message_id_list = [s['id'] for i in message_data for s in i['messages']]

            for message_id in handled_message_id_list:
                models.Message.update_read_flag(1, message_id)
        except:
            logging.exception('')

    @classmethod
    def __register_cluster_id(cls, message_data):
        message_id_list = []
        try:
            for data in message_data:
                message_id = [message['id'] for message in data['messages']]
                message_id_list.append({'user_id': data['user_id'], 'message_id': message_id})
        except:
            logging.exception('')

        # note: message_id_list = [{'user_id': 1, 'message_id': [1, 2]}, {'user_id': 2, 'message_id': [3]}]
        for i in message_id_list:
            # note: i = {'user_id': 1, 'message_id': [1, 2]}
            try:
                models.MessageCluster.register_new_message_cluster(i['user_id'])

                cluster_id = models.MessageCluster.find_id_by_user_id(i['user_id'])

                models.Message.tag_messages_with_cluster_id(i['message_id'], cluster_id)
            except:
                logging.exception('')
