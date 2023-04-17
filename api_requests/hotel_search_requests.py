import requests
import os
import json

SEARCH_URL = "https://hotels4.p.rapidapi.com/locations/v3/search"


headers = {
        "X-RapidAPI-Key": os.getenv('RAPID_API_KEY'),
        "X-RapidAPI-Host": os.getenv('RAPID_API_HOST')
    }


def cities_request(city: str):
    querystring = {"q": city, "locale": "ru_RU"}
    response = requests.request("GET", SEARCH_URL, headers=headers, params=querystring)

    response_json = json.loads(response.text)
    return response_json
