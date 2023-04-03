from loader import bot
from telebot.types import Message


@bot.message_handler(commands=['hello_world'])
def hello_world(message: Message) -> None:
    """
    Функция для отправки сообщения пользователю в ответ на команду
    "/hello_world"

    :param message: Сообщение поступающее от пользователя
    """
    bot.send_message(message.from_user.id, 'Hello world!')
