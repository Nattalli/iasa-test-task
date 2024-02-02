from django.urls import path

from .views import CityListView, CountryAverageView, WeatherDataView, CountryListView, CityByCountryListView

urlpatterns = [
    path('city/', CityListView.as_view(), name='cities'),
    path('cities/<str:country>/', CityByCountryListView.as_view(), name='city_list_by_country'),
    path('countries/', CountryListView.as_view(), name='country_list'),
    path('country-average/<str:country>/', CountryAverageView.as_view(), name='country_average_data'),
    path('weather-data/<str:lat>/<str:lng>/', WeatherDataView.as_view(), name='weather_historical_data'),
]
