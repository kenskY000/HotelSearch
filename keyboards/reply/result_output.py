from telebot import types


def result_output_buttons() -> types.ReplyKeyboardMarkup:
    """
    Функция для вывода кнопок для выбора способа сортировки результатов.
    :return: Markup объект, т.е. три кнопки
    """
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton("От самых дешевых к самым дорогим"))
    markup.add(types.KeyboardButton("От самых дорогих к самым дешевым"))
    markup.add(types.KeyboardButton("Выбрать диапазон цен"))
    return markup
