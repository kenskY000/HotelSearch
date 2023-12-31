from loader import bot
from telebot.types import Message
from database.core import crud
from database.models import db, History


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
    """
    Хендлер, отлавливающий выполнение команды /history, отправляет пользователю
    сообщение с историей запросов.
    :param message: Сообщение от пользователя
    """
    db_read = crud.retrieve()
    data = db_read(db, History, History.request)
    for elem in data:
        bot.send_message(message.from_user.id, str(elem.request))
