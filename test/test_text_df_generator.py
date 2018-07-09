import unittest

from core.nlp.df_generator.original_df_generator import OriginalDFGenerator


class TestTextDFGenerator(unittest.TestCase):
    def setUp(self):
        print('setup')

    def test_add_pos_tag_to_df(self):
        input_value = [['i', 'am', 'sad', '.']]
        actual = OriginalDFGenerator.create_original_df_by_w_toks(input_value)
        print('output--------------')
        print(actual)

    def test_add_pos_tag_to_df2(self):
        input_value = [
            ['i', 'feel', 'like', 'sad', 'because', 'Michael', 'did', 'not', 'know', 'really', 'who', 'he', 'liked',
             'but', 'all', 'ok', ','], ['However', ',', 'it', 'was', 'terrible', '.'], ['I', 'am', 'so', 'sad', 'so', 'i', 'cry', '.']]
        actual = OriginalDFGenerator.create_original_df_by_w_toks(input_value)
        print('output--------------')
        print(actual)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
