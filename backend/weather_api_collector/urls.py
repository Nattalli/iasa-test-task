from django.urls import path

from .views import CityListView, CountryAverageView

urlpatterns = [
    path('city/', CityListView.as_view(), name='city_list_api'),
    path('country-average/<str:country>/', CountryAverageView.as_view(), name='country_average_api'),
]
