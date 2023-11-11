import unittest
from bill_buddies import app

class TestUtilityRatesAPIIntegration(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_real_api_data(self):
        # Make a real API request
        response = self.app.get('/sorted-utility-rates/48104')  # Example ZIP code
        self.assertEqual(response.status_code, 200)

        # Check if the data format is as expected
        data = response.get_json()

        print(data[:3])

        # Add more assertions as needed to validate the data

if __name__ == '__main__':
    unittest.main()
