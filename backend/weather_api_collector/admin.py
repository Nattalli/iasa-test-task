from django.contrib import admin
from .models import WeatherData, City


admin.site.register(WeatherData)
admin.site.register(City)
