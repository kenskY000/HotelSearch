from loader import bot
from telebot.types import Message
from states.hotel_search_states import HotelSearchState
from api_requests import hotel_search_requests
from keyboards.inline import cities
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import datetime


@bot.message_handler(commands=['hotel_search'])
def hotel_search(message: Message) -> None:
    """
    Функция для запуска поиска отелей. Выводит пользователю сообщение
    с просьбой ввести город.

    :param message: Сообщение поступающее от пользователя
    """
    bot.set_state(message.from_user.id, HotelSearchState.location, message.chat.id)
    bot.send_message(message.from_user.id, f'Введите город, в котором хотите найти отель')


@bot.message_handler(state=HotelSearchState.location)
def get_location(message: Message) -> None:
    response = hotel_search_requests.cities_request(message.text)

    cities_dict = {}
    for i_var in range(len(response['sr'])):
        if response['sr'][i_var]['type'] == 'CITY':
            city_name = response['sr'][i_var]['regionNames']['fullName']
            city_id = response['sr'][i_var]['gaiaId']
            cities_dict[city_name] = city_id

    bot.send_message(
        message.from_user.id,
        'Уточните локацию',
        reply_markup=cities.city_buttons(cities_dict)
    )


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    bot.send_message(callback.message.chat.id,
                     f'Город выбран, теперь выберите дату заселения')
    #bot.set_state(callback.message.from_user.id, HotelSearchState.check_in, callback.message.chat.id)

    with bot.retrieve_data(callback.message.chat.id) as data:
        data['location_id'] = callback.data
    bot.answer_callback_query(callback.id)


# @bot.message_handler(state=HotelSearchState.check_in)
# def check_in(m):
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(callback.message.chat.id,
                     f"Select {LSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    result, key, step = DetailedTelegramCalendar(min_date=datetime.today(), locale='ru').process(c.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"You selected {result}",
                              c.message.chat.id,
                              c.message.message_id)
        bot.set_state(c.message.chat.id, HotelSearchState.check_in, c.message.chat.id)
