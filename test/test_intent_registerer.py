import unittest


class TestGenerateResponses(unittest.TestCase):
    def setUp(self):
        print('setup')

    def test_generate_responses(self):
        # negative keyword case
        input_value = 'i am sad.'
        print(input_value)
        actual = IntentRegisterer.request_to_apiai(input_value)
        print('\n' + 'output--------------')
        print(actual)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
