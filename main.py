from core.models.message import Message
from core.models.therapy_session import TherapySession
from core.models.user import User
from core.nlp.bot.factory.bot_factory import BotFactory


def main(message_data):
    user = User(message_data['user_id'])
    message = Message(message_data['messages'], user.id)
    therapy_session = TherapySession(user.id)

    bot = BotFactory.create(user, message, therapy_session)
    bot.reply()

    message.mark_done()
