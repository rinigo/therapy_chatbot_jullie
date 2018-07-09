import copy
import logging
from abc import ABC, abstractmethod


class BaseResponseGenerator(ABC):
    response_data_format = {'regular': [], 'quick_reply': []}

    def __init__(self, user, message, message_type=None):
        try:
            self.user = user
            self.message = message
            self.response_data = copy.deepcopy(BaseResponseGenerator.response_data_format)
            self.message_type = message_type
        except:
            logging.exception('')


    @abstractmethod
    def __call__(self, **arguments):
        pass

    def set_regular_response(self, response: list):
        self.response_data['regular'] = response

    def set_quick_reply(self, quick_reply_data):
        self.response_data['quick_reply'] = quick_reply_data

    def get_error_response_data(self):
        logging.exception('')
        return self.response_data
