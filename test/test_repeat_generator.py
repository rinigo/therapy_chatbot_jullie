import unittest

from core.nlp.response_generator.repeat_generator import RepeatGenerator


class TestRepeatGenerator(unittest.TestCase):
    def setUp(self):
        print('setup')

    def test_repeat_no_matched_message(self):
        message = 'i am nothing for him.'

        from nltk import word_tokenize, sent_tokenize

        s_tok = sent_tokenize(message)
        print(s_tok)

        w_tok = [word_tokenize(i) for i in s_tok]
        print(w_tok)

        list_for_df = [[sidx, widx, word] for sidx, s in enumerate(w_tok) for widx, word in enumerate(s)]
        print(list_for_df)

        text_df = pd.DataFrame(list_for_df)
        print(text_df)
        text_df.columns = ['sidx', 'widx', 'word']

        replaced_message = RepeatGenerator.__replace_word_from_csv(text_df)
        print(replaced_message)

        actual = RepeatGenerator.__repeat_no_matched_message(replaced_message)
        print('\n' + 'output--------------')
        print(actual)

    def test_repeat_short_message(self):
        message = 'i am sad.'

        from nltk import word_tokenize, sent_tokenize

        s_tok = sent_tokenize(message)
        print(s_tok)

        w_tok = [word_tokenize(i) for i in s_tok]
        print(w_tok)

        list_for_df = [[sidx, widx, word] for sidx, s in enumerate(w_tok) for widx, word in enumerate(s)]
        print(list_for_df)

        text_df = pd.DataFrame(list_for_df)
        print(text_df)
        text_df.columns = ['sidx', 'widx', 'word']

        replaced_message = RepeatGenerator.__replace_word_from_csv(text_df)
        print(replaced_message)

        actual = RepeatGenerator.__repeat_short_message(replaced_message)
        print('\n' + 'output--------------')
        print(actual)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
