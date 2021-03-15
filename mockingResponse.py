import requests
import unittest
from unittest import mock

# This is the class we want to test
class MyGreatClass:
    def fetch_json(self, url):
        response = requests.get(url)
        return response.json()

# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    print(args[0].split("/"))
    if args[0].split("/")[-2] == 'listings':
        return MockResponse({
            "objective": "rent",
            "propertyTypes": [
                "apartmentUnitFlat"
            ],
            "status": "live",
            "saleMode": "rent",
            "channel": "residential",
            "addressParts": {
                "stateAbbreviation": "vic",
                "displayType": "fullAddress",
                "streetNumber": "318",
                "unitNumber": "3703",
                "street": "Russell Street",
                "suburb": "Melbourne",
                "postcode": "3000",
                "displayAddress": "3703/318 Russell Street, Melbourne VIC 3000"
            },
            "advertiserIdentifiers": {
                "advertiserType": "agency",
                "advertiserId": 11842,
                "contactIds": [
                    1704046
                ],
                "agentIds": [
                    "A116989"
                ]
            },
            "apmIdentifiers": {
            "suburbId": 25807
            },
          "bathrooms": 1,
          "bedrooms": 2,
          "carspaces": 0,
          "dateAvailable": "2021-03-04",
          "dateUpdated": "2021-03-12T03:22:28.063Z",
          "dateListed": "2021-03-04T04:40:56Z",
            "priceDetails": {
                "canDisplayPrice": False,
                "displayPrice": "$550 per week"
            },
            "propertyId": "WP-3470-MQ",
            "rentalDetails": {
                "rentalMethod": "rent",
                "source": "internal",
                "canDisplayPrice": False
            },

        }, 200)


    return MockResponse(None, 404)
