from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from weather_api_collector.models import City


class CityListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.city1 = City.objects.create(
            city="Kyiv",
            lat=52,
            lng=31,
            country="Ukraine",
            population=100000
        )

    def test_city_list_view(self):
        url = reverse('cities')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['city'], 'A Coruña')

    def test_city_list_view_search(self):
        url = reverse('cities') + '?search=Kyiv'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['city'], 'Kyiv')


class WeatherDataViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.city = City.objects.create(
            city="Kyiv",
            lat=52,
            lng=31,
            country="Ukraine",
            population=100000
        )

    def test_weather_data_view(self):
        url = reverse('weather_historical_data', kwargs={'lat': str(self.city.lat), 'lng': str(self.city.lng)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('forecast_data', response.data)
        self.assertIn('key_indicators', response.data)
        self.assertIn('sentence', response.data)
        self.assertIn('rmse', response.data)
        self.assertIn('mae', response.data)
        self.assertIn('mre', response.data)
