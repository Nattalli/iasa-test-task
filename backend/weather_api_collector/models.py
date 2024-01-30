from django.db import models


class WeatherData(models.Model):
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now=True)
    temperature = models.FloatField()
    humidity = models.FloatField()


class City(models.Model):
    city = models.CharField(max_length=255)
    city_ascii = models.CharField(max_length=255)
    lat = models.FloatField()
    lng = models.FloatField()
    country = models.CharField(max_length=255)
    iso2 = models.CharField(max_length=2)
    iso3 = models.CharField(max_length=3)
    admin_name = models.CharField(max_length=255)
    capital = models.CharField(max_length=255)
    population = models.FloatField()
