from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS


def set_default_commands(bot):
    """
    Функция обозначающая, что элементы кортежа DEFAULT_COMMANDS
    являются командами для бота.

    :param bot:
    :return:
    """
    bot.set_my_commands(
        [BotCommand(*i) for i in DEFAULT_COMMANDS]
    )
