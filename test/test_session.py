import unittest
from unittest import TestCase


class TestGenerateResponses(TestCase):
    def setUp(self):
        print('setup')

    @staticmethod
    def set_session_finish_time(latest_session):
        try:
            latest_session.finish_at = datetime.utcnow() + timedelta(minutes=30)
            session.commit()
        except:
            session.rollback()
            logging.exception('')

    def test_set_session_finish_time(self):
        input_value = {2: [{'message': 'i am sad.', 'id': 2}]}
        self.base_generate_responses(input_value)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
