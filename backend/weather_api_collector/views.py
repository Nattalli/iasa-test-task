from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta
from django.db.models import Avg
from rest_framework import generics
from rest_framework.response import Response

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

        start_date = request.query_params.get('start_date', (datetime.now() - relativedelta(years=1)).strftime('%Y-%m-%d'))
        end_date = request.query_params.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        api_url = f"https://archive-api.open-meteo.com/v1/era5?latitude={lat}&longitude={lng}&start_date={start_date}&end_date={end_date}&hourly=temperature_2m"

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            weather_data = response.json()
            return Response(weather_data)
        except requests.exceptions.RequestException as e:
            return Response({'error': f'Request to open-meteo API failed: {str(e)}'}, status=500)
