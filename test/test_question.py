from core.nlp.question import question
import unittest
import pandas as pd
from core.nlp.normalizer import message_normalizer
import nltk
import string
import logging

"""
run specific function like this at Python Console. If you wanna make original test list, use test_question_answer_by_original_text_list

run test/test_question.py TestQuestion.test_question_answer_by_original_text_list

"""

class TestQuestion(unittest.TestCase):
    def setUp(self):
        pass

    @unittest.skip("モジュール修正中のためスキップ")
    def test_question_type(self):
        test_df = pd.read_csv("test/question_test.csv", error_bad_lines=False)
        print(len(test_df))

        def check_text_expectation(row):
            try:
                text = \
                message_normalizer.MessageNormalizer.normalize_message_for_question([nltk.word_tokenize(row["text"])])[
                    0]
                text = "".join(
                    [" " + i if not i.startswith("'") and i not in string.punctuation else i for i in text]).strip()
                reply = question.Test(text)
                print("structure_type: " + reply.result.structure_type)
                print("class_name: " + reply.result.class_name)
                print("auxiliary_verb: " + reply.result.auxiliary_verb)
                print("vo: " + reply.result.vo)
                print("svo: " + reply.result.svo)
                print("savo: " + reply.result.savo)
                print(reply.text)
                print(reply.result.answer)
                self.assertEqual(reply.result.structure_type, row["structure"])
                self.assertEqual(reply.result.class_name, row["class"])

            except Exception:
                logging.exception("Error")

        # for index, row in test_df.iterrows():
        #     check_text_expectation(row)

    @unittest.skip("モジュール修正中のためスキップ")
    def test_question_answer(self):
        test_df = pd.read_csv("test/question_test.csv", error_bad_lines=False)
        def check_text_expectation(row):
            try:
                tokenized = \
                message_normalizer.MessageNormalizer.normalize_message_for_question([nltk.word_tokenize(row["text"])])[
                    0]
                print("Original Text")
                print(tokenized)
                reply = question.Test(tokenized)
                # print("DF")
                # print(reply.result.df_info.df)
                # print("structure_type: " + reply.result.structure_type)
                # print("class_name: " + reply.result.class_name)
                # print("auxiliary_verb: " + reply.result.auxiliary_verb)
                # print("q_type: " + reply.result.df_info.q_type)
                # print("subject: " + reply.result.subject)
                # print("verb_original_form: " + reply.result.verb_original_form)
                # print("objective: " + reply.result.objective)
                print("ANSWER")
                print(reply.result.answer)
            except Exception:
                logging.exception("Error")

        for index, row in test_df[test_df.type == "should"].iterrows():
            check_text_expectation(row)

    def test_question_answer_by_original_text_list(self):
        def check_text_expectation(text):
            try:
                tokenized = \
                message_normalizer.MessageNormalizer.normalize_message_for_question([nltk.word_tokenize(text)])[
                    0]
                print("Original Text")
                print(tokenized)
                reply = question.Test(tokenized)
                print("ANSWER")
                print(reply.result.answer)
            except Exception:
                logging.exception("Error")


        text_list = ["Whats your gender?","Can you please talk with me right now?", "So what do you like to do with your free time?",
                     "Huh?",
                     "How can I say it to them?😭"]

        for text in text_list:
            check_text_expectation(text)


    @unittest.skip("モジュール修正中のためスキップ")
    def test_question_to_Jullie(self):
        text_list = ["are you jullie?"]

        try:
            for text in text_list:
                text = message_normalizer.MessageNormalizer.normalize_message_for_question([nltk.word_tokenize(text)])[
                    0]
                text = "".join(
                    [" " + i if not i.startswith("'") and i not in string.punctuation else i for i in text]).strip()
                reply = question.Test(text)
                print("class_name: " + reply.result.class_name)
                print(reply.text)
                print(reply.result.answer)

        except Exception:
            logging.exception("Error")

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
