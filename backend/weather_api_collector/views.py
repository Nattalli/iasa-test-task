from datetime import datetime

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from django.db.models import Avg
from rest_framework import generics
from rest_framework.response import Response
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from .models import City
from .serializers import CitySerializer, CountryAverageSerializer, CountrySerializer
from .utils import generate_sentence, calculate_mae, calculate_mre, calculate_rmse


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


class CountryListView(generics.ListAPIView):
    queryset = City.objects.values('country').distinct().order_by('country')
    serializer_class = CountrySerializer
    pagination_class = None


class CityByCountryListView(generics.ListAPIView):
    serializer_class = CitySerializer
    pagination_class = None

    def get_queryset(self):
        country = self.kwargs['country']
        return City.objects.filter(country__iexact=country).order_by('city')


class WeatherDataView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        city = City.objects.filter(city=self.kwargs.get('city')).first()
        lat = city.lat
        lng = city.lng

        if not lat or not lng:
            return Response({'error': 'Latitude and longitude parameters are required'}, status=400)

        start_date = request.query_params.get('start_date',
                                              (datetime.now() - relativedelta(years=1)).strftime('%Y-%m-%d'))
        end_date = request.query_params.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        api_url = f"https://archive-api.open-meteo.com/v1/era5?latitude={lat}&longitude={lng}&start_date={start_date}&end_date={end_date}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            weather_data = response.json()

            data = {
                'time': weather_data['hourly']['time'],
                'temperature_2m': weather_data['hourly']['temperature_2m'],
                'relative_humidity_2m': weather_data['hourly']['relative_humidity_2m'],
                'wind_speed_10m': weather_data['hourly']['wind_speed_10m']
            }

            df = pd.DataFrame(data)
            df = df.dropna()

            df['time'] = pd.to_datetime(df['time'])
            df.columns = ['ds', 'temperature_2m', 'relative_humidity_2m', 'wind_speed_10m']

            model_holtwinters = ExponentialSmoothing(df['temperature_2m'], seasonal='add', seasonal_periods=24)
            fit_model_holtwinters = model_holtwinters.fit()
            forecast_holtwinters = fit_model_holtwinters.forecast(steps=24)

            forecast_data_holtwinters = pd.DataFrame(
                {'time': pd.date_range(start=(datetime.now() + relativedelta(days=1)).strftime('%Y-%m-%d'), periods=24,
                                       freq='h'),
                 'temperature_2m': forecast_holtwinters})

            model_arima = ARIMA(df['temperature_2m'], order=(1, 1, 1))
            fit_model_arima = model_arima.fit()
            forecast_arima = fit_model_arima.get_forecast(steps=24)

            forecast_data_arima = pd.DataFrame(
                {'time': pd.date_range(start=(datetime.now() + relativedelta(days=1)).strftime('%Y-%m-%d'), periods=24,
                                       freq='h'),
                 'temperature_2m': forecast_arima.predicted_mean})

            response_data = {
                'forecast_data': {
                    'time': {
                        'holtwinters': forecast_data_holtwinters['time'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                        'arima': forecast_data_arima['time'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    },
                    'temperature_2m': {
                        'holtwinters': forecast_data_holtwinters['temperature_2m'].values.tolist(),
                        'arima': forecast_data_arima['temperature_2m'].values.tolist(),
                    }
                }
            }

            key_indicators = df[['temperature_2m', 'relative_humidity_2m', 'wind_speed_10m']].describe()
            response_data['key_indicators'] = key_indicators.to_dict()

            sentence = generate_sentence(response_data['key_indicators'])
            response_data['sentence'] = sentence

            real_api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"

            response_real = requests.get(real_api_url)
            response_real.raise_for_status()
            real_weather_data = response_real.json()

            real_temperature = real_weather_data['hourly']['temperature_2m']

            real_temperature_for_comparison = real_temperature[-24:]

            rmse_holtwinters = calculate_rmse(forecast_data_holtwinters['temperature_2m'],
                                              real_temperature_for_comparison)
            mae_holtwinters = calculate_mae(forecast_data_holtwinters['temperature_2m'],
                                            real_temperature_for_comparison)
            mre_holtwinters = calculate_mre(forecast_data_holtwinters['temperature_2m'],
                                            real_temperature_for_comparison)

            rmse_arima = calculate_rmse(forecast_data_arima['temperature_2m'], real_temperature_for_comparison)
            mae_arima = calculate_mae(forecast_data_arima['temperature_2m'], real_temperature_for_comparison)
            mre_arima = calculate_mre(forecast_data_arima['temperature_2m'], real_temperature_for_comparison)

            response_data['rmse'] = {
                'holtwinters': rmse_holtwinters,
                'arima': rmse_arima
            }
            response_data['mae'] = {
                'holtwinters': mae_holtwinters,
                'arima': mae_arima
            }
            response_data['mre'] = {
                'holtwinters': mre_holtwinters if mre_holtwinters != -1 else 0,
                'arima': mre_arima if mre_arima != -1 else 0,
            }

            return Response(response_data)

        except requests.exceptions.RequestException as e:
            return Response({'error': f'Request to open-meteo API failed: {str(e)}'}, status=500)
