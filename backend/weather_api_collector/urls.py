from django.urls import path
from .views import WeatherDataRetrieveView, HistoricalWeatherDataView

urlpatterns = [
    path('weather/', WeatherDataRetrieveView.as_view(), name='weather-data'),
    path(
        'weather/historical/<str:city>/<str:country>/',
        HistoricalWeatherDataView.as_view(),
        name='historical-weather-data'
    ),
]
