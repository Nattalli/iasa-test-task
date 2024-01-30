import requests
from datetime import datetime, timedelta
from config.settings import OPEN_WEATHER_TOKEN, OPEN_WEATHER_API_URL
from weather_api_collector.models import WeatherData


def fetch_and_update_weather_data(city, country, weather_data=None):
    url = f'{OPEN_WEATHER_API_URL}data/2.5/weather?q={city},{country}&appid={OPEN_WEATHER_TOKEN}'

    response = requests.get(url)
    data = response.json()

    if 'main' in data:
        temperature = data['main']['temp']
        humidity = data['main']['humidity']

        if weather_data is None:
            weather_data = WeatherData(city=city, country=country)

        weather_data.temperature = temperature
        weather_data.humidity = humidity
        weather_data.date = datetime.now()

        weather_data.save()


def update_weather_data_from_last_update(city, country):
    try:
        weather_data = WeatherData.objects.get(city=city, country=country)
        last_update_date = weather_data.date
        today_date = datetime.now().date()

        if last_update_date.date() < today_date:
            while last_update_date.date() < today_date:
                last_update_date += timedelta(days=1)
                fetch_and_update_weather_data(city, country, weather_data)
    except WeatherData.DoesNotExist:
        fetch_and_update_weather_data(city, country)


def get_historical_weather_data(city, country, date):
    timestamp = int(date.timestamp())

    url = f'{OPEN_WEATHER_API_URL}data/2.5/onecall/timemachine?lat={city}&lon={country}&dt={timestamp}&appid={OPEN_WEATHER_TOKEN}'
    print(url)

    response = requests.get(url)
    data = response.json()

    return data
