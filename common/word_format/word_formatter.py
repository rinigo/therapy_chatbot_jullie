from nltk import word_tokenize, sent_tokenize
import logging


class WordFormatter:
    @staticmethod
    def WToks2Str(w_toks):
        try:
            text = ''
            for sent in w_toks:
                text += WordFormatter.SingleWToks2Str(sent)

            return text
        except Exception:
            logging.exception('Error at: ' + str(__name__))
            return ''

    @staticmethod
    def SingleWToks2Str(w_tok):
        try:
            return ''.join(
                '' if word == ''
                else ' ' + str(word) if all(c.isdigit() for c in word)
                else str(word) if all(not c.isalpha() for c in word)
                else ' ' + str(word) + '.' if widx == len(w_tok) - 1 and any(c.isalpha() for c in word)
                else ' ' + str(word)
                for widx, word in enumerate(w_tok)
            )
        except Exception:
            logging.exception('Error at: ' + str(__name__))
            return ''

    @staticmethod
    def SToks2WToks(s_toks):
        try:
            return [word_tokenize(s) for s in s_toks]
        except Exception:
            logging.exception('Error at: ' + str(__name__))
            return [[]]

    @staticmethod
    def Df2WToks(text_df, column_name="word"):
        try:
            if text_df is None:
                return []

            w_toks = []
            for idx, sidx in enumerate(list(set(text_df.sidx.tolist()))):
                w_toks.append([])

                for word in text_df.loc[text_df.sidx == sidx, column_name].tolist():
                    w_toks[idx].append(word)

            return w_toks
        except Exception:
            logging.exception('Error at: ' + str(__name__))
            return [[]]

    @staticmethod
    def Df2Str(text_df):
        try:
            w_toks = WordFormatter.Df2WToks(text_df)

            text = WordFormatter.WToks2Str(w_toks)

            return text
        except Exception:
            logging.exception('Error at: ' + str(__name__))
            return ''

    @staticmethod
    def Series2Str(series):
        try:
            return " ".join([word for word in series])
        except Exception:
            logging.exception('Error at: ' + str(__name__))
            return ''

    @staticmethod
    def MsgDict2WToks(message_dicts):
        try:
            s_toks = [d['text'] for d in message_dicts]
            w_toks = WordFormatter.SToks2WToks(s_toks)

            return w_toks
        except Exception:
            logging.exception('Error at: ' + str(__name__))
            return [[]]

    @staticmethod
    def Str2WToks(text):
        try:
            s_toks = sent_tokenize(text)
            w_toks = [word_tokenize(s) for s in s_toks]

            return w_toks
        except Exception:
            logging.exception('Error at: ' + str(__name__))
            return [[]]
