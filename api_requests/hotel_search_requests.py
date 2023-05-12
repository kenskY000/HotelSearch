from typing import List
import requests
import os
import json
from loguru import logger

logger.add("debug.log", format="{time} {level} {message}",
           level="DEBUG")


def headers():
    """
    Функция для загрузки переменных окружения.
    :return: Словарь с переменными окружения.
    """
    return {
            "X-RapidAPI-Key": os.getenv('RAPID_API_KEY'),
            "X-RapidAPI-Host": os.getenv('RAPID_API_HOST')
        }


@logger.catch
def cities_request(city: str):
    """
    Функция для отправки GET-запроса к API.
    :param city: Город, вводимый пользователем.
    :return: JSON, содержащий несколько разных городов.
    """
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": city, "locale": "ru_RU"}
    response_json = None
    try:
        response = requests.request("GET", url, headers=headers(),
                                    params=querystring, timeout=10)
        if response.status_code != requests.codes.ok:
            logger.error(response.status_code)
        else:
            response_json = json.loads(response.text)
    except requests.RequestException as exc:
        logger.error(f'ERROR cities_request -> {exc}')
    if response_json is not None:
        return response_json
    else:
        logger.error('ERROR cities_request -> response is empty!')


@logger.catch
def hotels_request_custom(region_id: str, check_in_date: dict,
                          check_out_date: dict, adults: int,
                          children: list, min_price: int, max_price: int):
    """
    Функция для отправки POST запроса к API. Возвращает список отелей в
    диапазоне заданных цен.
    :param region_id: ID города
    :param check_in_date: Дата заезда
    :param check_out_date: Дата выезда
    :param adults: Количество взрослых
    :param children: Количество детей
    :param min_price: Минимальная стоимость отеля за ночь
    :param max_price: Максимальная стоимость отеля за ночь
    :return: JSON, содержащий разные предложения отелей, в диапазоне заданной
    цены
    """
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "destination": {"regionId": region_id},
        "checkInDate": check_in_date,
        "checkOutDate": check_out_date,
        "rooms": [
            {
                "adults": adults,
                "children": children
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 10,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {
            "price": {
                "max": max_price,
                "min": min_price
            },
            'availableFilter': 'SHOW_AVAILABLE_ONLY'
        }
    }

    response_json = None
    try:
        response = requests.request("POST", url, json=payload,
                                    headers=headers(), timeout=10)

        if response.status_code != requests.codes.ok:
            logger.error(response.status_code)
        else:
            response_json = json.loads(response.text)

    except requests.RequestException as exc:
        logger.error(f'ERROR hotels_request_custom -> {exc}')

    if response_json is not None:
        return response_json
    else:
        logger.error('ERROR hotels_request_custom -> response is empty!')


@logger.catch
def hotels_request(region_id: str, check_in_date: dict, check_out_date: dict,
                   adults: int, children: list):
    """
    Функция для отправки POST запроса к API. Возвращает список отелей в
    диапазоне заданных цен.
    :param region_id: ID города
    :param check_in_date: Дата заезда
    :param check_out_date: Дата выезда
    :param adults: Количество взрослых
    :param children: Количество детей
    :return: JSON, содержащий разные предложения отелей, отсортированные по
    возрастанию цены
    """
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    payload = {
        "currency": "RUB",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "destination": {"regionId": region_id},
        "checkInDate": check_in_date,
        "checkOutDate": check_out_date,
        "rooms": [
            {
                "adults": adults,
                "children": children
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 10,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {'availableFilter': 'SHOW_AVAILABLE_ONLY'}
    }
    response_json = None
    try:
        response = requests.request("POST", url, json=payload,
                                    headers=headers(), timeout=10)

        if response.status_code != requests.codes.ok:
            logger.error(response.status_code)
        else:
            response_json = json.loads(response.text)

    except requests.RequestException as exc:
        logger.error(f'ERROR hotels_request_custom -> {exc}')

    if response_json is not None:
        return response_json
    else:
        logger.error('ERROR hotels_request_custom -> response is empty!')


@logger.catch
def images_request(hotel: str) -> List:
    """
    Функция для запроса картинок по-заданному ID отеля.
    :param hotel: ID отеля
    :return: JSON, содержащий подробную информацию об отеле, из которого
    в дальнейшем можно вытянуть изображения отеля
    """
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    payload = {
        "currency": "RUB",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "propertyId": hotel
    }
    images = None

    try:
        response = requests.request("POST", url, json=payload,
                                    headers=headers(), timeout=10)
        if response.status_code != requests.codes.ok:
            logger.error(response.status_code)
        else:
            response_json = json.loads(response.text)

            images = []
            for item in range(5):
                image_url = (
                    response_json['data']['propertyInfo']['propertyGallery']
                    ['images'][item]['image']['url']
                )
                images.append(image_url)

    except requests.RequestException as exc:
        logger.error(f'ERROR images_request -> {exc}')

    if images:
        return images
    else:
        logger.error('ERROR images_request -> No images found!')
