from typing import List
import requests
import os
import json
from loguru import logger

logger.add("debug.log", format="{time} {level} {message}",
           level="DEBUG")
headers = {
        "X-RapidAPI-Key": os.getenv('RAPID_API_KEY'),
        "X-RapidAPI-Host": os.getenv('RAPID_API_HOST')
    }


def cities_request(city: str):
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": city, "locale": "ru_RU"}
    response = requests.request("GET", url, headers=headers,
                                params=querystring, timeout=10)

    response_json = json.loads(response.text)
    return response_json


def hotels_request_custom(region_id: str, check_in_date: dict, check_out_date: dict,
                   adults: int, children: list, min_price: int, max_price: int):

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

    response = requests.request("POST", url, json=payload,
                                headers=headers, timeout=10)
    response_json = json.loads(response.text)
    return response_json


def hotels_request(region_id: str, check_in_date: dict, check_out_date: dict,
                   adults: int, children: list, sort_method: str):

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
        "sort": sort_method,
        "filters": {'availableFilter': 'SHOW_AVAILABLE_ONLY'}
    }

    response = requests.request("POST", url, json=payload,
                                headers=headers, timeout=10)
    response_json = json.loads(response.text)
    return response_json


@logger.catch
def images_request(hotel: str) -> List:
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    payload = {
        "currency": "RUB",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "propertyId": hotel
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    # TODO: проверьте пожалуйста правильно ли я реализовал логирование?
    #  Если такой пример годится, то добавлю еще
    try:
        if response.status_code != requests.codes.ok:
            raise Exception
    except Exception:
        logger.error(response.status_code)

    response_json = json.loads(response.text)

    images_list = []
    for item in range(5):
        image_url = (
            response_json['data']['propertyInfo']['propertyGallery']
            ['images'][item]['image']['url']
        )
        images_list.append(image_url)

    return images_list
