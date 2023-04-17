from keyboards.reply.contact import request_contact
from loader import bot
from states.contact_information import UserInfoState
from telebot.types import Message


@bot.message_handler(commands=['survey'])
def survey(message: Message) -> None:
    """
    Функция для запуска опросника. Предлагает пользователю ввести
    своё имя.

    :param message: Сообщение поступающее от пользователя
    """
    bot.set_state(message.from_user.id, UserInfoState.name, message.chat.id)
    bot.send_message(message.from_user.id, f'Привет, {message.from_user.username} введи своё имя')


@bot.message_handler(state=UserInfoState.name)
def get_name(message: Message) -> None:
    """
    Функция записывает введённое пользователем имя(message) в поле name
    класса UserInfoState. Если параметр message содержит только буквы,
    то имя записывается в соответствующее поле name контекстного менеджера data.

    :param message: Сообщение поступающее от пользователя
    """
    if message.text.isalpha():
        bot.send_message(message.from_user.id, 'Спасибо, записал. Теперь введи свой возраст')
        bot.set_state(message.from_user.id, UserInfoState.age, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Имя может содержать только буквы')


@bot.message_handler(state=UserInfoState.age)
def get_age(message: Message) -> None:
    """
    Функция записывает введённый пользователем возраст(message) в поле age
    класса UserInfoState. Если параметр message содержит только цифры,
    то имя записывается в поле age контекстного менеджера data.

    :param message: Сообщение поступающее от пользователя
    """
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Спасибо, записал. Теперь введи страну проживания')
        bot.set_state(message.from_user.id, UserInfoState.country, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['age'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Возраст может быть только числом')


@bot.message_handler(state=UserInfoState.country)
def get_country(message: Message) -> None:
    """
    Функция записывает введённую пользователем страну(message) в поле country
    контекстного менеджера data.

    :param message: Сообщение поступающее от пользователя
    """
    bot.send_message(message.from_user.id, 'Спасибо, записал. Теперь введи свой город')
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['country'] = message.text


@bot.message_handler(state=UserInfoState.city)
def get_city(message: Message) -> None:
    """
    Функция записывает введённый пользователем город(message) в поле city
    контекстного менеджера data.
    Также функция отправляет пользователю запрос на отправку контактных данных.

    :param message: Сообщение поступающее от пользователя
    """
    bot.send_message(message.from_user.id,
                     'Спасибо, записал. Теперь отправь свой номер, нажав на кнопку',
                     reply_markup=request_contact())
    bot.set_state(message.from_user.id, UserInfoState.phone_number, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = message.text


@bot.message_handler(content_types=['text', 'contact'], state=UserInfoState.phone_number)
def get_contact(message: Message) -> None:
    """
    Функция выводит введённые пользователем данные на всех этапах опросника.

    :param message: Сообщение поступающее от пользователя
    """
    if message.content_type == 'contact':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['phone_number'] = message.contact.phone_number

            text = (f'Спасибо за предоставленную информацию, ваши данные: \n'
                    f'Имя - {data["name"]}\n'
                    f'Возраст - {data["age"]}\n'
                    f'Страна - {data["country"]}\n'
                    f'Город - {data["city"]}\n'
                    f'Номер телефона - {data["phone_number"]}')
            bot.send_message(message.from_user.id, text)
            bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Чтобы отправить контактную информацию на кнопку')
