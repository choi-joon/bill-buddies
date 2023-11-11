import unittest
from unittest.mock import patch
import bill_buddies
import json

class UtilityRatesTestCase(unittest.TestCase):
    def setUp(self):
        # Configure your Flask app for testing
        bill_buddies.app.config['TESTING'] = True
        # Create a test client
        self.app = bill_buddies.app.test_client()

    @patch('requests.get')
    def test_get_sorted_utility_rates(self, mock_get):
        # Make a GET request to your route
        response = self.app.get('/sorted-utility-rates/12345')

        # Check the status code and response data
        self.assertEqual(response.status_code, 200)
        sorted_rates = json.loads(response.data)
        print(sorted_rates)
        mock_get.return_value.status_code = 500
        response = self.app.get('/sorted-utility-rates/12345')
        self.assertEqual(response.status_code, 500)
        error_response = json.loads(response.data)
        self.assertEqual(error_response, {'error': 'Failed to fetch data'})

if __name__ == '__main__':
    unittest.main()
