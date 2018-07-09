import unittest


class TestSuicideDetector(unittest.TestCase):
    def setUp(self):
        print('setup')

    def test_get_suicide_flag(self):
        from core.models.user import User
        from core.models.message import Message
        from core.nlp.normalizer.message_normalizer import MessageNormalizer

        # negative keyword case
        input_value = {1: [{'message': 'i want to die.', 'id': 16}]}
        print(input_value[1][0]['message'])

        user = User(1)
        message = Message(input_value[1], user)
        message = MessageNormalizer.normalize_message_by_w_toks()
        message = message.get_message_details()
        print(message.text_df)
        my_sd = SuicideDetector(message)
        actual = my_sd.is_suicidal()
        expected = True
        self.assertEqual(expected, actual)

    def test_get_suicide_flag2(self):
        from core.models.user import User
        from core.models.message import Message
        from core.nlp.normalizer.message_normalizer import MessageNormalizer

        # negative keyword case
        input_value = {1: [{'message': 'i do not want to die.', 'id': 16}]}
        print(input_value[1][0]['message'])

        user = User(1)
        message = Message(input_value[1], user)
        message = MessageNormalizer(message).normalize_message_by_w_toks()
        message = message.get_message_details()
        print(message.text_df)
        my_sd = SuicideDetector(message)
        actual = my_sd.is_suicidal()
        expected = False
        self.assertEqual(expected, actual)

    def test_get_suicide_flag3(self):
        from core.models.user import User
        from core.models.message import Message
        from core.nlp.normalizer.message_normalizer import MessageNormalizer

        # negative keyword case
        input_value = {1: [{'message': 'i do not want to live anymore', 'id': 16}]}
        print(input_value[1][0]['message'])

        user = User(1)
        message = Message(input_value[1], user)
        message = MessageNormalizer(message).normalize_message_by_w_toks()
        message = message.get_message_details()
        print(message.text_df)
        my_sd = SuicideDetector(message)
        actual = my_sd.is_suicidal()
        expected = True
        self.assertEqual(expected, actual)

    def test_get_suicide_flag4(self):
        from core.models.user import User
        from core.models.message import Message
        from core.nlp.normalizer.message_normalizer import MessageNormalizer

        # negative keyword case
        input_value = {1: [{'message': 'he wants to die', 'id': 16}]}
        print(input_value[1][0]['message'])

        user = User(1)
        message = Message(input_value[1], user)
        message = MessageNormalizer(message).normalize_message_by_w_toks()
        message = message.get_message_details()
        print(message.text_df)
        my_sd = SuicideDetector(message)
        actual = my_sd.is_suicidal()
        expected = False
        self.assertEqual(expected, actual)

    def test_get_suicide_flag5(self):
        from core.models.user import User
        from core.models.message import Message
        from core.nlp.normalizer.message_normalizer import MessageNormalizer

        # negative keyword case
        input_value = {1: [{'message': 'I think he wants to die.', 'id': 16}]}
        print(input_value[1][0]['message'])

        user = User(1)
        message = Message(input_value[1], user)
        message = MessageNormalizer(message).normalize_message_by_w_toks()
        message = message.get_message_details()
        print(message.text_df)
        my_sd = SuicideDetector(message)
        actual = my_sd.is_suicidal()
        expected = False
        self.assertEqual(expected, actual)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()