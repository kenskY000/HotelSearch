from telebot import types
from typing import Dict


def city_buttons(cities: Dict) -> types.InlineKeyboardMarkup:
    """
    Функция создающая инлайновую клавиатуру для уточнения города
    :param cities: Словарь городов, состоящий из пары Город: ID города
    :return: Markup объект, тобишь клавитура.
    """
    markup = types.InlineKeyboardMarkup()
    for city_name, city_id in cities.items():
        markup.add(types.InlineKeyboardButton(city_name,
                                              callback_data=city_id))
    return markup


