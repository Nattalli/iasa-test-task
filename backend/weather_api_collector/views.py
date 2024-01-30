from django.db.models import Avg
from django.http import JsonResponse

from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response

from .models import City
from .models import WeatherData
from .serializers import CitySerializer, CountryAverageSerializer
from .serializers import WeatherDataSerializer
from .utils import update_weather_data_from_last_update


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


class CountryAverageView(generics.RetrieveAPIView):
    serializer_class = CountryAverageSerializer

    def get(self, request, *args, **kwargs):
        country = self.kwargs.get('country')
        if not country:
            return Response({'error': 'Country parameter is missing'}, status=400)

        average_values = City.objects.filter(country=country).aggregate(
            average_lat=Avg('lat'),
            average_lng=Avg('lng')
        )

        serializer = self.get_serializer(average_values)
        return Response(serializer.data)
