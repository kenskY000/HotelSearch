from loader import bot
from telebot.types import Message


@bot.message_handler(commands=['hello_world'])
def hello_world(message: Message) -> None:
    bot.send_message(message.from_user.id, 'Hello world!')
