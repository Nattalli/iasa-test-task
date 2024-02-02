import unittest
import numpy as np

from weather_api_collector.utils import calculate_rmse, calculate_mae, calculate_mre, generate_sentence


class TestWeatherFunctions(unittest.TestCase):

    def test_calculate_rmse(self):
        predictions = np.array([2, 4, 7, 9])
        targets = np.array([1, 3, 8, 10])
        self.assertEqual(calculate_rmse(predictions, targets), 1.0)

    def test_calculate_mae(self):
        predictions = np.array([2, 4, 7, 9])
        targets = np.array([1, 3, 8, 10])
        self.assertEqual(calculate_mae(predictions, targets), 1.0)

    def test_calculate_mre(self):
        predictions = np.array([2, 4, 7, 9])
        targets = np.array([1, 3, 8, 10])
        expected_mre = (abs(predictions - targets) / targets).mean()
        self.assertEqual(calculate_mre(predictions, targets), expected_mre)

    def test_calculate_mre_with_inf(self):
        predictions = np.array([2, 4, 7, 9])
        targets = np.array([0, 0, 0, 0])
        self.assertEqual(calculate_mre(predictions, targets), -1)

    def test_generate_sentence(self):
        key_indicators = {
            'relative_humidity_2m': {'mean': 40.5},
            'wind_speed_10m': {'mean': 5.3, 'std': 1.2}
        }
        expected_sentence = ("The humidity has been around 40.50%. The wind speed has been averaging 5.30 m/s with "
                             "a 1.20 m/s variation.")
        self.assertEqual(generate_sentence(key_indicators), expected_sentence)

