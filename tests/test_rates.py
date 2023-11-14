import unittest
import json
from bill_buddies import app

class TestUtilityRatesAPIIntegration(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_real_api_data(self):
        response = self.app.get('/sorted-utility-rates/90081')  # Example ZIP code
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        print(json.dumps(data, indent=4))

        response1 = self.app.get('/sorted-utility-rates/91911')  # Example ZIP code
        self.assertEqual(response1.status_code, 200)
        data = response1.get_json()
        print(json.dumps(data, indent=4))

if __name__ == '__main__':
    unittest.main()
