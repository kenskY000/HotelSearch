from telebot.types import Message

from loader import bot


@bot.message_handler(state=None)
def bot_echo(message: Message):
    """
    Эхо хендлер, куда летят текстовые сообщения без указанного состояния

    :param message: Сообщение поступающее от пользователя
    """
    bot.reply_to(
        message, f"Эхо без состояния или фильтра.\n Сообщение: {message.text}"
    )
