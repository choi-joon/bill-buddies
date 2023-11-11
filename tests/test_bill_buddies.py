import unittest
from unittest.mock import patch
from bill_buddies import app  # Import the Flask app instance

class TestGetSortedUtilityRates(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('bill_buddies.views.index.requests.get')  # Adjust the patch target based on your structure
    def test_get_sorted_utility_rates_success(self, mock_get):
        # Mocking successful API response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'rate': 0.12}, {'rate': 0.10}, {'rate': 0.15}
        ]

        # Test successful response
        response = self.app.get('/sorted-utility-rates/90275')
        data = response.get_json()

        print("Response JSON:", data)

        # Assertions for successful case
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
        self.assertEqual(data, [{'rate': 0.10}, {'rate': 0.12}, {'rate': 0.15}])

    @patch('bill_buddies.views.index.requests.get')  # Adjust the patch target based on your structure
    def test_get_sorted_utility_rates_failure(self, mock_get):
        # Mocking failed API response
        mock_response = mock_get.return_value
        mock_response.status_code = 404
        mock_response.json.return_value = {'error': 'Failed to fetch data'}

        # Test failed response
        response = self.app.get('/sorted-utility-rates/12345')
        data = response.get_json()

        # Assertions for failure case
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(data, {'error': 'Failed to fetch data'})

if __name__ == '__main__':
    unittest.main()
