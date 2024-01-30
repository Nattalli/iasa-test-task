from rest_framework import serializers
from .models import WeatherData, City


class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['city', 'lat', 'lng']


class CountryAverageSerializer(serializers.Serializer):
    average_lat = serializers.FloatField()
    average_lng = serializers.FloatField()
