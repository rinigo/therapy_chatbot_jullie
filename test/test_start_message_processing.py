import unittest
from unittest import TestCase
# from core.nlp.start_message_processing import start_message_processing
from core.models.user import User


class TestGenerateResponses(TestCase):
    def setUp(self):
        print('setup')

    def test_generate_responses(self):
        input_value = {2: [{'message': 'i am sad.', 'id': 2}]}
        self.base_generate_responses(input_value)

    def test_generate_responses_positive(self):
        input_value = {2: [{'message': 'i am happy.', 'id': 2}]}
        self.base_generate_responses(input_value)

    def test_generate_responses_n_and_p(self):
        input_value = {2: [{'message': 'i am sad but i am happy.', 'id': 9}]}
        self.base_generate_responses(input_value)

    def test_generate_responses_special(self):
        input_value = {2: [{'message': 'i am lonely.', 'id': 9}]}
        self.base_generate_responses(input_value)

    def test_generate_responses_neutral(self):
        input_value = {2: [{'message': 'i am nothing for him.', 'id': 2}]}
        self.base_generate_responses(input_value)

    def test_generate_responses_neutral_negative(self):
        input_value = {2: [{'message': 'i am nothing for him.', 'id': 9}, {'message': 'i am sad.', 'id': 20}]}
        self.base_generate_responses(input_value)

    def test_generate_responses_neutral_positive(self):
        input_value = {2: [{'message': 'i am nothing for him.', 'id': 9}, {'message': 'but i am happy', 'id': 20}]}
        self.base_generate_responses(input_value)

    def test_generate_responses_neutral_neutral(self):
        input_value = {2: [{'message': 'i am nothing for him.', 'id': 9}, {'message': 'I was just thinking about that.', 'id': 20}]}
        self.base_generate_responses(input_value)

    def test_generate_responses_neutral_special(self):
        input_value = {2: [{'message': 'i am nothing for him.', 'id': 9}, {'message': 'i want to cry', 'id': 20}]}
        self.base_generate_responses(input_value)

    def base_generate_responses(self, input_value):
        print(input_value[2][0]['message'])
        # actual = start_message_processing(input_value)
        print('\n' + 'output--------------')
        # print(actual)

    def test_generate_responses_hi(self):
        input_value = {2: [{'message': 'hi', 'id': 9}]}
        self.base_generate_responses(input_value)

    def test_generate_responses_hi_welcome(self):
        input_value = {2: [{'message': 'hi', 'id': 9}, {'message': 'you are welcome', 'id': 20}]}
        self.base_generate_responses(input_value)

    def test_generate_responses_thank_bye(self):
        input_value = {2: [{'message': 'thank you.', 'id': 9}, {'message': 'bye', 'id': 20}]}
        self.base_generate_responses(input_value)

    def test_generate_responses_hi_negative(self):
        input_value = {2: [{'message': 'hi', 'id': 9}, {'message': 'i am sad', 'id': 20}]}
        self.base_generate_responses(input_value)

    def test_generate_responses_hi_special(self):
        input_value = {2: [{'message': 'hi', 'id': 9}, {'message': 'i want to cry', 'id': 20}]}
        self.base_generate_responses(input_value)

    def test_generate_responses_hi_neutral(self):
        input_value = {2: [{'message': 'hi', 'id': 9}, {'message': 'i am nothing for him', 'id': 20}]}
        self.base_generate_responses(input_value)

    def test_generate_responses_suicide(self):
        input_value = {2: [{'message': 'i want to die', 'id': 9}]}
        self.base_generate_responses(input_value)
        User.update_status(2, 2)

    def test_generate_responses_many_sents(self):
        input_value = {2: [{'message': 'i am sad', 'id': 9}, {'message': 'i was thinking', 'id': 20}, {'message': 'i was bad', 'id': 22}, {'message': 'he knew that', 'id': 22}, {'message': 'i was totally mad', 'id': 23}]}
        self.base_generate_responses(input_value)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
