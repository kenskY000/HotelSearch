from loader import bot
from telebot import types
from telebot.types import Message, InputMediaPhoto, ReplyKeyboardRemove
from states.hotel_search_states import HotelSearchState
from api_requests import hotel_search_requests
from keyboards.inline import cities
from keyboards.reply import result_output
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date


@bot.message_handler(commands=['start'])
def hotel_search(message: Message) -> None:
    """
    Функция для запуска поиска отелей. Выводит пользователю сообщение
    с просьбой ввести город.
    :param message: Message
    :return: None
    """
    bot.set_state(message.from_user.id,
                  HotelSearchState.location,
                  message.chat.id)
    bot.send_message(message.from_user.id,
                     f'Введите город, в котором хотите найти отель',
                     reply_markup=ReplyKeyboardRemove())


@bot.message_handler(state=HotelSearchState.location)
def get_location(message: Message) -> None:
    """
    Уточнение локации в ответ на введённый город.
    :param message: Message
    :return: None
    """
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

    bot.set_state(message.from_user.id,
                  HotelSearchState.check_in,
                  message.chat.id)


@bot.callback_query_handler(func=lambda callback: callback.data.isdigit(),
                            state=HotelSearchState.check_in)
def callback_message(callback: types.CallbackQuery) -> None:
    """
    Колбэк, ловящий нажатие на инлайн кнопку, уточняющую город.
    Также выводит календарь для выбора даты заселения.
    :param callback: CallbackQuery
    :return: None
    """
    bot.send_message(callback.message.chat.id,
                     f'Город выбран. Теперь выберите дату заселения')

    with bot.retrieve_data(callback.message.chat.id) as data:
        data['location_id'] = callback.data

    calendar, step = DetailedTelegramCalendar(calendar_id=1,
                                              min_date=date.today(),
                                              locale='ru').build()
    bot.send_message(callback.message.chat.id,
                     f"Выберите {LSTEP[step]}",
                     reply_markup=calendar)

    bot.answer_callback_query(callback.id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def callback_message(callback: types.CallbackQuery) -> None:
    """
    Колбэк ловящий нажатие на инлайновый календарь.
    :param callback: CallbackQuery
    :return: None
    """
    result, key, step = (
        DetailedTelegramCalendar(
            calendar_id=1,
            min_date=date.today(),
            locale='ru')
        .process(callback.data)
    )

    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              callback.message.chat.id,
                              callback.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата заселения: {result}",
                              callback.message.chat.id,
                              callback.message.message_id)
        bot.set_state(callback.message.chat.id,
                      HotelSearchState.check_out,
                      callback.message.chat.id)
        bot.send_message(callback.message.chat.id,
                         f'Выберите дату выезда')
        check_in = {
            "day": result.day,
            "month": result.month,
            "year": result.year
        }
        with bot.retrieve_data(callback.message.chat.id) as data:
            data['check_in'] = check_in

        calendar, step = DetailedTelegramCalendar(calendar_id=2,
                                                  min_date=date.today(),
                                                  locale='ru').build()
        bot.send_message(callback.message.chat.id,
                         f"Выберите {LSTEP[step]}",
                         reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2),
                            state=HotelSearchState.check_out)
def callback_message(callback: types.CallbackQuery) -> None:
    """
    Колбэк ловящий нажатие на инлайновый календарь.
    :param callback: CallbackQuery
    :return: None
    """
    result, key, step = DetailedTelegramCalendar(
        calendar_id=2,
        min_date=date.today(),
        locale='ru').process(callback.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              callback.message.chat.id,
                              callback.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата выезда: {result}",
                              callback.message.chat.id,
                              callback.message.message_id)
        check_out = {
            "day": result.day,
            "month": result.month,
            "year": result.year
        }
        with bot.retrieve_data(callback.message.chat.id) as data:
            data['check_out'] = check_out
        bot.send_message(callback.message.chat.id,
                         f'Введите количество взрослых гостей')
        bot.set_state(callback.message.chat.id,
                      HotelSearchState.adult_guests,
                      callback.message.chat.id)


@bot.message_handler(state=HotelSearchState.adult_guests)
def adult_guests(message: Message) -> None:
    """
    Запоминает количество взрослых гостей, и спрашивает количество детей.
    :param message: Message
    :return: None
    """
    if message.text.isdigit():
        bot.set_state(message.from_user.id,
                      HotelSearchState.child_guests,
                      message.chat.id)
        bot.send_message(message.from_user.id,
                         f'Спасибо, записал. Теперь введите количество детей')

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['adult_guests'] = int(message.text)

    else:
        bot.send_message(message.from_user.id,
                         f'Количество взрослых должно быть одним числом!')


@bot.message_handler(state=HotelSearchState.child_guests)
def child_guests(message: Message) -> None:
    """
    Запоминает количество детей, если 0, то предлагает выбрать способ
    вывода результатов, если больше - предлагает ввести возраст детей через
    запятую.
    :param message: Message
    :return: None
    """
    if message.text.isdigit():
        if message.text == '0':
            with bot.retrieve_data(message.from_user.id,
                                   message.chat.id) as data:
                data['children'] = [{"age": 0}]

            bot.register_next_step_handler(message, result_print)
            bot.send_message(
                message.from_user.id,
                'Спасибо, записал. Теперь выберите способ вывода результатов',
                reply_markup=result_output.result_output_buttons()
            )

        else:
            bot.set_state(message.from_user.id,
                          HotelSearchState.child_age,
                          message.chat.id)
            bot.send_message(
                message.from_user.id,
                'Спасибо, записал. Теперь введите возраст детей через запятую'
            )

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['child_guests'] = int(message.text)

    else:
        bot.send_message(message.from_user.id,
                         f'Количество детей должно быть одним числом!')


@bot.message_handler(state=HotelSearchState.child_age)
def child_age(message: Message) -> None:
    """
    Запоминает возраст детей и предлагает выбрать способ вывода результатов.
    :param message: Message
    :return: None
    """
    child_age_list = []
    for age in message.text.split(','):
        child_age_list.append(int(age.strip()))

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        children = []
        for child in range(data['child_guests']):
            children.append({"age": child_age_list[child]})
        data['children'] = children

    bot.set_state(message.from_user.id,
                  HotelSearchState.sort_method,
                  message.chat.id)
    bot.send_message(message.from_user.id,
                     'Спасибо, записал. Теперь выберите '
                     'способ вывода результатов',
                     reply_markup=result_output.result_output_buttons())


@bot.message_handler(content_types='text')
def result_print(message: Message) -> None:
    """
    Функция для вывода результатов в зависимости от нажатой кнопки.
    :param message: Message
    :return: None
    """
    if message.text == 'От самых дешевых к самым дорогим':
        low_to_high(message)
    elif message.text == 'От самых дорогих к самым дешевым':
        high_to_low(message)
    elif message.text == 'Выбрать диапазон цен':
        bot.send_message(
            message.from_user.id,
            'Введите минимальную и максимальную цену '
            'через тире (в долларах)'
        )
        bot.register_next_step_handler(message, range_output)
        bot.set_state(
            message.from_user.id,
            HotelSearchState.custom_range,
            message.chat.id
        )


@bot.message_handler(state=HotelSearchState.custom_range)
def range_output(message: Message):
    """
    Вывод отелей в заданном ценовом диапазоне.
    :param message: Message
    :return: None
    """
    min_price = int(message.text.split('-')[0])
    max_price = int(message.text.split('-')[1])
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        response = hotel_search_requests.hotels_request_custom(
            data['location_id'],
            data['check_in'],
            data['check_out'],
            data['adult_guests'],
            data['children'],
            min_price,
            max_price
        )

    for item in range(10):
        properties = response['data']['propertySearch']['properties'][item]
        text = properties['name']
        hotel_id = properties['id']
        reviews = f'\nОценка пользователей: {properties["reviews"]["score"]}'
        price = (
            f"\nЦена за ночь: "
            f"{properties['price']['options'][0]['formattedDisplayPrice']}"
        )
        hotel_url = (
            f'\n\nПодробнее об отеле: '
            f'https://www.hotels.com/h{properties["id"]}.Hotel-Information'
        )
        msg = text + reviews + price + hotel_url
        images = hotel_search_requests.images_request(hotel_id)
        bot.send_media_group(
            message.chat.id,
            [InputMediaPhoto(photo, caption=msg) for photo in images]
        )
        bot.send_message(message.chat.id, msg)


def high_to_low(message):
    """
    Функция для переворота списка отелей. Для корректного отображения
    цен от высоких к низким.
    :param message: Message
    :return: None
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        response = hotel_search_requests.hotels_request(
            data['location_id'],
            data['check_in'],
            data['check_out'],
            data['adult_guests'],
            data['children'],
            sort_method='PRICE_LOW_TO_HIGH'
        )

    for item in range(9, -1, -1):
        properties = response['data']['propertySearch']['properties'][item]
        text = properties['name']
        hotel_id = properties['id']
        reviews = f'\nОценка пользователей: {properties["reviews"]["score"]}'
        price = (
            f"\nЦена за ночь: "
            f"{properties['price']['options'][0]['formattedDisplayPrice']}"
        )
        hotel_url = (
            f'\n\nПодробнее об отеле: '
            f'https://www.hotels.com/h{properties["id"]}.Hotel-Information'
        )
        msg = text + reviews + price + hotel_url
        images = hotel_search_requests.images_request(hotel_id)
        bot.send_media_group(
            message.chat.id,
            [InputMediaPhoto(photo, caption=msg) for photo in images]
        )
        bot.send_message(message.chat.id, msg)


def low_to_high(message: Message):
    """
    Функция для стандартного вывода отелей, от низких цен к высоким.
    :param message: Message
    :return: None
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        response = hotel_search_requests.hotels_request(
            data['location_id'],
            data['check_in'],
            data['check_out'],
            data['adult_guests'],
            data['children'],
            sort_method='PRICE_LOW_TO_HIGH'
        )

    for item in range(10):
        properties = response['data']['propertySearch']['properties'][item]
        text = properties['name']
        hotel_id = properties['id']
        reviews = f'\nОценка пользователей: {properties["reviews"]["score"]}'
        price = (
            f"\nЦена за ночь: "
            f"{properties['price']['options'][0]['formattedDisplayPrice']}"
        )
        hotel_url = (
            f'\n\nПодробнее об отеле: '
            f'https://www.hotels.com/h{properties["id"]}.Hotel-Information'
        )
        msg = text + reviews + price + hotel_url
        images = hotel_search_requests.images_request(hotel_id)
        bot.send_media_group(
            message.chat.id,
            [InputMediaPhoto(photo, caption=msg) for photo in images]
        )
        bot.send_message(message.chat.id, msg)
