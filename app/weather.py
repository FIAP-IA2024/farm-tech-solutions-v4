from dotenv import load_dotenv
import os
import requests

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather_data(city="Sao Paulo"):
    if not API_KEY:
        raise ValueError(
            "API Key não encontrada. Certifique-se de que está definida no arquivo .env."
        )

    params = {"q": city, "units": "metric", "appid": API_KEY}
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        weather_info = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
        }
        return weather_info
    else:
        print(
            f"Erro ao obter os dados meteorológicos ({response.status_code}): {response.text}"
        )
        return None
