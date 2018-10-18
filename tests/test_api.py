import unittest

from call_records import create_app


class TestApi(unittest.TestCase):

    """ Tests for API. """

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()

    def test_index(self):
        """ Tests that API route returns 200 and JSON mimetype. """
        rv = self.client.get('/')
        self.assertTrue(rv.data)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.mimetype, 'application/json')

if __name__ == '__main__':
    unittest.main()
