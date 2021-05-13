import json
import time

import requests


class Geocoding:
    """This class provides the mechanism for geocoding a standard U.S. address."""

    # Define base url
    __api_urls = {
        "base": "https://nominatim.openstreetmap.org/",
        "search": "search/",
        "status": "status.php"
    }

    @staticmethod
    def get_geocode(address):
        """
        Retrieves geocode of this address.
        """
        parameters = {
            "street": address.street,
            "city": address.city,
            "state": address.state,
            "country": address.country,
            "postcode": address.zipcode,
            "format": "geocodejson",
            "polygon_svg": 1
        }
        url = Geocoding.__api_urls['base'] + Geocoding.__api_urls['search']
        return requests.get(url=url, params=parameters)

    @staticmethod
    def get_geocodes(addresses: list):
        """Retrieves geocode coordinates for a list of addresses.

        :param addresses: List of addresses.
        :return: List of geocodes representing the geocode coordinates of address passed as arguments.
        A list of addresses whose geocodes could not be retrieved is also returned when applicable.
        """
        geocodes = []
        log = []
        for address in addresses:
            if not (address.latitude is None or address.longitude is None):
                geocodes.append(address.coordinates_as_string())
            else:
                log.append(address)
            time.sleep(1/10)
        return geocodes, log

    @staticmethod
    def connection():
        """Check server availability"""
        url = "{base}{status}?format={format}".format(base=Geocoding.__api_urls["base"],
                                                      status=Geocoding.__api_urls["status"],
                                                      format="json")
        return requests.get(url=url)

    @staticmethod
    def json_response(obj, sort=False, indent=4):
        """Create a formatted string of JSON object"""
        return json.dumps(obj, sort_keys=sort, indent=indent)
