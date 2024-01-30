from django.urls import path
from .views import WeatherDataRetrieveView, CityListView, CountryAverageView

urlpatterns = [
    path('weather/', WeatherDataRetrieveView.as_view(), name='weather-data'),
    path('city-list/', CityListView.as_view(), name='city_list_api'),
    path('country-average/<str:country>/', CountryAverageView.as_view(), name='country_average_api'),
]
