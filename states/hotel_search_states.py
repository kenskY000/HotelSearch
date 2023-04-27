from telebot.handler_backends import State, StatesGroup


class HotelSearchState(StatesGroup):
    """
    Класс для записи состояний во время опроса пользователя
    для составления корректного поискового запроса.
    """
    location = State()
    check_in = State()
    check_out = State()
    adult_guests = State()
    child_guests = State()
    child_age = State()
    sort_method = State()
    custom_range = State()
