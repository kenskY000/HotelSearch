from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    """
    Класс для описания состояний в опроснике бота. Содержит в себе
    инстансы класса State
    """
    name = State()
    age = State()
    country = State()
    city = State()
    phone_number = State()
