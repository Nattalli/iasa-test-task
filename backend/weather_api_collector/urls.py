from django.urls import path
from .views import WeatherDataRetrieveView, CityListView

urlpatterns = [
    path('weather/', WeatherDataRetrieveView.as_view(), name='weather-data'),
    path('city-list/', CityListView.as_view(), name='city_list_api'),
]
