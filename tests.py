import unittest
from ddt import ddt, data, unpack
from app import app
import requests
import json

@ddt
class FlaskListingTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    # test root path to confirm app is running
    def test_home_status_code(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

    def test_home_data(self):
        result = self.app.get('/')
        self.assertEqual(result.data, "hello world!")

    #test listings status
    def test_listings_status_code(self):
        result = self.app.get('/listings')
        self.assertEqual(result.status_code, 200)

    # test various search queries for validity of json & correctness

    # test for validity of geojson
    @data('/listings?min_price=100000&max_price=200000&min_bed=2&max_bed=2&min_bath=2&max_bath=2',
          '/listings?max_price=300000&min_bed=3&min_bath=2',
          '/listings?min_price=150000&max_price=250000&max_bed=4&max_bath=3',
          '/listings?min_bed=2&max_bed=3&per_page_max=40',
          '/listings?min_bed=2&max_bed=3&per_page_max=50&status=pending')
    def test_valid_geojson(self, url):
        result = self.app.get(url)
        # validate format of json by testing at geojsonlint.com
        validation_endpoint = 'http://geojsonlint.com/validate'
        geo_request = requests.post(validation_endpoint, data=result.data)
        self.assertEqual(geo_request.json()['status'], 'ok')

    #test counts against counts found by querying db directly
    @data(('/listings?min_price=100000&max_price=200000&min_bed=2&max_bed=2&min_bath=2&max_bath=2', 431),
          ('/listings?min_price=100000&max_price=200000&min_bed=2&max_bed=2&min_bath=2&max_bath=2&page=5', 31),
          ('/listings?max_price=300000&min_bed=3&min_bath=2', 4992),
          ('/listings?min_price=150000&max_price=250000&max_bed=4&max_bath=3', 3786),
          ('/listings?min_bed=2&max_bed=3&per_page_max=40', 40),
          ('/listings?min_bed=2&max_bed=3&per_page_max=50&status=pending', 50))
    @unpack
    def test_correct_results(self, url, count):
        result = self.app.get(url)
        feature_collection = json.loads(result.data)
        num_listings = len(feature_collection["features"])
        self.assertEqual(num_listings, count)

    # test for presence and correctness of optional pagination links
    @data(('/listings?min_price=100000&max_price=200000&page=3', 3),
          ('/listings?max_price=300000&min_bed=3&min_bath=2&page=10', 10),
          ('/listings?min_price=150000&max_price=250000&max_bed=4&max_bath=3&per_page_max=50', 1))
    @unpack
    def test_correct_pagination_links(self, url, page):
        result = self.app.get(url)
        feature_collection = json.loads(result.data)
        self.assertEqual(feature_collection["page"], page)
        self.assertIsNotNone(feature_collection["links"])
        self.assertIsNotNone(feature_collection["links"]["first"])
        self.assertIsNotNone(feature_collection["links"]["last"])

    @data('/listings?min_price=100000&max_price=110000',
          '/listings?min_price=275000&max_price=300000&min_bed=3&min_bath=2')
    def test_no_pagination_without_params(self, url):
        result = self.app.get(url)
        feature_collection = json.loads(result.data)
        self.assertRaises(KeyError, lambda: feature_collection["links"])

    @data(('/listings?status=sold&max_per_page=10', "sold", "FF0000"),
          ('/listings?status=pending&max_per_page=10', "pending", "FFFF00"),
          ('/listings?status=active&max_per_page=10', "active", "009900"),)
    @unpack
    def test_correct_status_and_color(self, url, status, color):
        result = self.app.get(url)
        feature_collection = json.loads(result.data)
        features = feature_collection["features"]
        assert all(f["properties"]["status"] == status for f in features)
        assert all(f["properties"]["marker-color"] == color for f in features)


if __name__ == '__main__':
    unittest.main()
