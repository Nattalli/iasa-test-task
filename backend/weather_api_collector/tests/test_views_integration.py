from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from weather_api_collector.models import City


class IntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.city = City.objects.create(
            city="Kyiv",
            lat=52,
            lng=31,
            country="Ukraine",
            population=100000
        )

    def test_integration_city_weather_data(self):
        url = reverse('weather_historical_data', kwargs={'lat': str(self.city.lat), 'lng': str(self.city.lng)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('forecast_data', response.data)
        self.assertIn('key_indicators', response.data)
        self.assertIn('sentence', response.data)
        self.assertIn('rmse', response.data)
        self.assertIn('mae', response.data)
        self.assertIn('mre', response.data)
