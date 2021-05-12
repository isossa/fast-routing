from Geocoding import *


class Address(object):
    """This class provides the mechanism for working building stand U.S. addresses.

    It provides methods for geocoding standard U.S. addresses. Standard U.S. addresses
    are defined to have the following formats:

        street, state, country, zipcode.

    Attributes:

    """

    def __init__(self, street="", city="", state="", country="United States", zipcode=""):
        """Creates a standard U.S address.

        Args:
            street:
                String representing the street number. String will be UTF-8 encoded.
            city:
                String representing the city. String will be UTF-8 encoded.
            state:
                String representing the state. String will be UTF-8 encoded.
            country:
                Optional; String representing the country. String will be UTF-8 encoded.
                Default: United States of America.
            zipcode:
                Integer representing the zipcode.
        """
        self.__street = street
        self.__city = city
        self.__state = state
        self.__country = country
        self.__zipcode = zipcode
        self.__latitude = None
        self.__longitude = None
        self.__info = None

    @property
    def street(self) -> str:
        """Retrieves the street of this address.

        Returns:
            String representing the street of this address.
        """
        return self.__street

    @property
    def city(self) -> str:
        """Retrieves the city in which this address is located.

        Returns:
            String representing the city in which this address is located.
        """
        return self.__city

    @property
    def state(self) -> str:
        """Retrieves the state in which this address is located.

        Returns:
            String representing the state in which this address is located.
        """
        return self.__state

    @property
    def country(self) -> str:
        """Retrieves the country in which this address is located.

        Returns:
            String representing the country in which this address is located.
        """
        return self.__country

    @property
    def zipcode(self) -> str:
        """Retrieves the zipcode in which this address is located.

        Returns:
            String representing the zipcode in which this address is located.
        """
        return self.__zipcode

    @property
    def latitude(self) -> float:
        """Retrieves the latitude of this address.

        Returns:
            Floating point representing the latitude of this address.
        """
        if self.__latitude is None:
            self.__geocode(self)
        return self.__latitude

    @property
    def longitude(self) -> float:
        """Retrieves the longitude of this address.

        Returns:
            Floating point representing the longitude of this address.
        """
        if self.__longitude is None:
            self.__geocode(self)
        return self.__longitude

    @property
    def info(self) -> dict:
        """Retrieves additional geocoding information about this address.

        Returns:
            Dict of additional information about this address.
        """
        if self.__info is None:
            self.__geocode(self)
        return self.__info

    @property
    def coordinates(self) -> tuple:
        """Retrieves latitude and longitude of this address.

        Returns:
            A pair representing the latitude and longitude of this address.
        """
        if self.__info is None:
            self.__geocode(self)
        return self.__latitude, self.__longitude

    def coordinates_as_string(self):
        """Retrieves coordinates as string separated pair"""
        lat, long = self.coordinates
        return f'{lat}, {long}'

    @staticmethod
    def __geocode(self):
        """Set geocode coordinates of this address."""

        if self.__info is None:
            self.__info = Geocoding.get_geocode(self).json()

            try:
                longitude, latitude = tuple(self.__info['features'][0]['geometry']['coordinates'])

                if latitude < -90 or latitude > 90:
                    raise ValueError("Illegal argument, latitude must be between -90 and 90")

                if longitude < -180 or longitude > 180:
                    raise ValueError("Illegal argument, longitude must be between -180 and 180")

                self.__latitude = latitude
                self.__longitude = longitude
            except (BaseException, Exception):
                self.__latitude = None
                self.__longitude = None

    @staticmethod
    def build_addresses(data):
        """Given a data frame, returns a list of Address objects"""
        return [Address(street=add.Address.strip(), city=add.City.strip(), state=add.State.strip(),
                        zipcode=add.Zip_Code, country="United States") for add in data.itertuples()]

    def __str__(self) -> str:
        """Retrieves a string representation of this address.

        Returns:
            String representing this address. The string is formatted as follows:
            "STREET, CITY, STATE, COUNTRY, ZIPCODE"
        """
        return '{street}, {city}, {state}, {country}, {zipcode}'.format(street=self.__street, city=self.__city,
                                                                        state=self.__state, country=self.__country,
                                                                        zipcode=self.__zipcode)

    def __eq__(self, other):
        return (
                self.__class__ == other.__class__ and self.street == other.street and self.city == other.city
                and self.state == other.state and self.country == other.country and self.zipcode == other.zipcode
        )

    def __hash__(self):
        return hash(self.coordinates)


