import unittest
import http.client
import json
import settings


class CurrencyExchangeTest(unittest.TestCase):

    def setUp(self):
        self.client = http.client.HTTPConnection(settings.TEST_HOST, settings.TEST_PORT)
        self.response = {}

    def tearDown(self):
        self.response.close()

    def test_get(self):
        self.client.request(method='GET', url='')
        self.response = self.client.getresponse()
        code = json.loads(self.response.read().decode())['code']
        self.assertEqual(405, code)

    def test_post(self):
        body = {"curr_from": "usd", "curr_to": "rub", "number": 100}
        self.client.request(method='POST', url='', body=json.dumps(body).encode())
        self.response = self.client.getresponse()
        resp_keys = json.loads(self.response.read().decode()).keys()
        self.assertIn('usd', resp_keys)
        self.assertIn('rub', resp_keys)


if __name__ == '__main__':
    unittest.main()
