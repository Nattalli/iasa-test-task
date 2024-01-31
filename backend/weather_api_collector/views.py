from datetime import datetime

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from django.db.models import Avg
from rest_framework import generics
from rest_framework.response import Response
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from .models import City
from .serializers import CitySerializer, CountryAverageSerializer


class CityListView(generics.ListAPIView):
    serializer_class = CitySerializer

    def get_queryset(self):
        queryset = City.objects.order_by('city')
        search_query = self.request.query_params.get('search', '').capitalize()
        if search_query:
            queryset = queryset.filter(city__icontains=search_query)
        return queryset


class CountryAverageView(generics.RetrieveAPIView):
    serializer_class = CountryAverageSerializer

    def get(self, request, *args, **kwargs):
        country = self.kwargs.get('country')
        if not country:
            return Response({'error': 'Country parameter is missing'}, status=400)

        average_values = City.objects.filter(country=country.capitalize()).aggregate(
            average_lat=Avg('lat'),
            average_lng=Avg('lng')
        )

        serializer = self.get_serializer(average_values)
        return Response(serializer.data)


class WeatherDataView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        lat = self.kwargs.get('lat')
        lng = self.kwargs.get('lng')

        if not lat or not lng:
            return Response({'error': 'Latitude and longitude parameters are required'}, status=400)

        # Оригінальний запит на прогноз
        start_date = request.query_params.get('start_date',
                                              (datetime.now() - relativedelta(years=1)).strftime('%Y-%m-%d'))
        end_date = request.query_params.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        api_url = f"https://archive-api.open-meteo.com/v1/era5?latitude={lat}&longitude={lng}&start_date={start_date}&end_date={end_date}&hourly=temperature_2m"

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            weather_data = response.json()

            data = {'time': weather_data['hourly']['time'], 'temperature_2m': weather_data['hourly']['temperature_2m']}
            df = pd.DataFrame(data)
            df = df.dropna()

            df['time'] = pd.to_datetime(df['time'])
            df.columns = ['ds', 'temperature_2m']

            model = ExponentialSmoothing(df['temperature_2m'], seasonal='add', seasonal_periods=24)
            fit_model = model.fit()
            forecast = fit_model.forecast(steps=24)

            forecast_data = pd.DataFrame(
                {'time': pd.date_range(start=df['ds'].max(), periods=24, freq='h'), 'temperature_2m': forecast})

            response_data = {
                'forecast_data': {
                    'time': forecast_data['time'].dt.strftime('%Y-%m-%d %H:%M:%S').values.tolist(),
                    'temperature_2m': forecast_data['temperature_2m'].values.tolist()
                }
            }

            key_indicators = df[['temperature_2m']].describe()
            response_data['key_indicators'] = key_indicators.to_dict()

            additional_api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&past_days=10&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
            additional_response = requests.get(additional_api_url)
            additional_response.raise_for_status()
            additional_weather_data = additional_response.json()

            additional_data = {
                'time': additional_weather_data['hourly']['time'],
                'temperature_2m': additional_weather_data['hourly']['temperature_2m'],
                'relative_humidity_2m': additional_weather_data['hourly']['relative_humidity_2m'],
                'wind_speed_10m': additional_weather_data['hourly']['wind_speed_10m']
            }

            additional_df = pd.DataFrame(additional_data)
            additional_df = additional_df.dropna()

            additional_df['time'] = pd.to_datetime(additional_df['time'])
            additional_df.columns = ['ds', 'temperature_2m', 'relative_humidity_2m', 'wind_speed_10m']

            additional_key_indicators = additional_df[['temperature_2m', 'relative_humidity_2m', 'wind_speed_10m']].describe()
            response_data['additional_key_indicators'] = additional_key_indicators.to_dict()

            sentence = generate_sentence(response_data['key_indicators'])
            response_data['sentence'] = sentence

            return Response(response_data)

        except requests.exceptions.RequestException as e:
            return Response({'error': f'Request to open-meteo API failed: {str(e)}'}, status=500)


def generate_sentence(key_indicators):
    temperature_mean = key_indicators['temperature_2m']['mean']
    temperature_range = key_indicators['temperature_2m']['max'] - key_indicators['temperature_2m']['min']
    temperature_std = key_indicators['temperature_2m']['std']

    if temperature_std < 5:
        temperature_variation = "stably"
    elif temperature_std < 10:
        temperature_variation = "moderately"
    else:
        temperature_variation = "significantly"

    sentence = f"The temperature has been averaging around {temperature_mean:.2f}°C with a {temperature_variation} {temperature_std:.2f}°C variation over time. The temperature range has been between {temperature_mean - temperature_range/2:.2f}°C and {temperature_mean + temperature_range/2:.2f}°C."

    return sentence
