import logging
from common.constant.admin_command import AdminCommand
from common.word_format.word_formatter import WordFormatter
from core.nlp.df_generator.sentiment_score_df_generator import SentimentScoreDFGenerator
from core.nlp.df_generator.original_df_generator import OriginalDFGenerator
from core.nlp.df_generator.text_kw_df_generator import TextKwDFGenerator
from core.nlp.intent.intent_checker import IntentChecker
from core.nlp.normalizer.message_normalizer import MessageNormalizer


class MessagePreprocessor:
    def __call__(self, message, user):
        try:
            if self.__exists_admin_command(message, user):
                return message

            w_toks = WordFormatter.MsgDict2WToks(message.message_dicts)
            message.original_df = OriginalDFGenerator.create_original_df_by_w_toks(w_toks)

            message_normalizer = MessageNormalizer()
            message.text_df = message_normalizer(message.message_dicts, user.sender_id)

            intent_checker = IntentChecker()
            message.intent_list = intent_checker(message.text_df)

            text_kw_df_generator = TextKwDFGenerator()
            message.text_kw_df = text_kw_df_generator(message.text_kw_df)

            sentiment_score_df_generator = SentimentScoreDFGenerator()
            message.sentiment_score_df = sentiment_score_df_generator(message.text_df, message.text_kw_df)

            return message
        except:
            logging.exception('')
            return message

    def __exists_admin_command(self, message, user):
        try:
            text = [i['text'] for i in message.message_dicts][0]
            exists_admin_command = text in AdminCommand.admin_command_list.value

            is_from_admin_user = user.first_name in {"Yuya", "Rintaro"}

            return exists_admin_command and is_from_admin_user
        except:
            logging.exception('')
            return False
