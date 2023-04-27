from telebot import types
from typing import Dict


def city_buttons(cities: Dict) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    for city_name, city_id in cities.items():
        markup.add(types.InlineKeyboardButton(city_name,
                                              callback_data=city_id))
    return markup


