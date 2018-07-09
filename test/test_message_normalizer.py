import pandas as pd
import unittest
from nltk import sent_tokenize, word_tokenize
from core.nlp.normalizer.message_normalizer import MessageNormalizer


class TestMessageNormalizer(unittest.TestCase):
    def setUp(self):
        print('setup')

    @staticmethod
    def test_remove_unimportant_words_at_tail():
        text = 'I am very stressed as I am in y9 and trying to do well'
        s_toks = sent_tokenize(text)
        w_toks = [word_tokenize(s) for s in s_toks]
        df = pd.DataFrame(w_toks)
        df.columns = ['sidx','widx','word', 'pos', 'base_form']
        MessageNormalizer.remove_unimportant_words_at_tail(df)
        return

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
