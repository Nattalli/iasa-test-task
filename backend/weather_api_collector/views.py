from datetime import datetime, timedelta

from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import City
from .models import WeatherData
from .serializers import CitySerializer
from .serializers import WeatherDataSerializer
from .utils import update_weather_data_from_last_update, get_historical_weather_data


class WeatherDataRetrieveView(generics.RetrieveAPIView):
    queryset = WeatherData.objects.all()
    serializer_class = WeatherDataSerializer

    def retrieve(self, request, *args, **kwargs):
        city = self.kwargs['city']
        country = self.kwargs['country']

        update_weather_data_from_last_update(city, country)

        try:
            weather_data = WeatherData.objects.get(city=city, country=country)
            serialized_data = WeatherDataSerializer(weather_data).data
            return JsonResponse(serialized_data)
        except WeatherData.DoesNotExist:
            return JsonResponse({'detail': 'Weather data not found.'}, status=404)


class CityListView(generics.ListAPIView):
    serializer_class = CitySerializer

    def get_queryset(self):
        queryset = City.objects.order_by('city')
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(city__icontains=search_query)
        return queryset
