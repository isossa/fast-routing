import random
import sys
from enum import Enum

from . import database
from . import services
from . import utils


class Role(Enum):
    PERMANENT = 'Permanent'
    VOLUNTEER = 'Volunteer'
    NONE = 'None'


class Address:
    """This class provides the mechanism for working building stand U.S. addresses.

    It provides methods for geocoding standard U.S. addresses. Standard U.S. addresses
    are defined to have the following formats:

        street, state, country, zipcode.

    Attributes:
    """

    def __init__(self, street="", city="", state="", country="United States", zipcode="", is_home_base=""):
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
        if is_home_base == "":
            self.__is_home_base = 0
        else:
            self.__is_home_base = int(is_home_base) == 1

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
    def is_home_base(self) -> bool:
        """Returns whether this address is a home base."""
        return self.__is_home_base

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
            self.__info = services.Geocoding.get_geocode(self).json()

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
        print('BUILD ADDRESSES')
        print(data)
        return [Address(street=add.Address.strip(), city=add.City.strip(), state=add.State.strip(),
                        zipcode=add.Zip_Code, country="United States", is_home_base=add.Home_Base)
                for add in data.itertuples()]

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


class Location:
    def __init__(self, address: Address, demand: int, identifier: str):
        self._address: Address = address
        self._demand: int = demand
        self._identifier = identifier
        self._is_assigned = False

    @property
    def address(self):
        return self._address

    @property
    def demand(self):
        return self._demand

    @property
    def identifier(self):
        return self._identifier

    @property
    def is_assigned(self):
        return self._is_assigned

    def set_status(self, status: bool):
        self._is_assigned = status

    def __str__(self):
        info = f'Address: {self._address}\n' \
               f'Demand: {self._demand}'
        return info


class Route:
    def __init__(self, route: list):
        """

        :param route:
        """
        self._route = route
        self._demand = 0
        self._distance = 0

    @property
    def route(self):
        """

        :return:
        """
        return self._route

    @property
    def demand(self):
        """

        :return:
        """
        if self._demand == 0:
            return self.__get_demand()

        return self._demand

    @property
    def distance(self):
        """

        :return:
        """
        self._distance = 0
        for index in range(len(self._route) - 1):
            location1 = self._route[index]
            location2 = self._route[index + 1]

            self._distance += database.DistanceMatrixDB.distance_between(location1.identifier, location2.identifier)

        return self._distance

    def add_location(self, location: Location):
        self._route.append(location)
        location.set_status(True)

    def remove_location(self, location: Location):
        if location in self._route:
            self._route.remove(location)
            location.set_status(False)

    def __get_demand(self):
        """

        :return:
        """
        for location in self._route:
            self._demand += location.demand

        return self._demand

    def __str__(self):
        """

        :return:
        """
        str_representation = [str(location.identifier) for location in self._route]
        return ' - '.join(str_representation) if len(self._route) > 0 else 'None'


class Driver:
    def __init__(self, first_name: str, last_name: str, role: Role):
        """

        :param first_name:
        :param last_name:
        :param role:
        """
        self._first_name: str = first_name
        self._last_name: str = last_name
        self._availability_list: list = list()
        self._availability_score: int = 0
        self._route: Route = Route(route=list())
        self._role = role

    @property
    def role(self):
        """

        :return:
        """
        return self._role

    @property
    def first_name(self):
        """

        :return:
        """
        return self._first_name

    @property
    def last_name(self):
        """

        :return:
        """
        return self._last_name

    @property
    def availability_list(self):
        """

        :return:
        """
        return self._availability_list

    @property
    def availability_score(self):
        """

        :return:
        """
        if self._availability_score == 0:
            return self.__get_availability_score()

        return self._availability_score

    @property
    def route(self):
        """

        :return:
        """
        if self._route is None:
            return self.__get_route()
        return self._route

    def __str__(self):
        """

        :return:
        """
        info = f'Name: {self._first_name} {self._last_name}\n' \
               f'ID: {self._id}\n' \
               f'Role: {self._role.value}\n' \
               f'Route Assigned: {self._route}\n' \
               f'Availability Score: {self._availability_score}'
        return info

    def set_availability(self, availability: list):
        """

        :param availability:
        :return:
        """
        if availability.count(0) + availability.count(1) != len(availability):
            raise ValueError('Availability must have values either 0 (available) or 1 (not available)')

        self._availability_list = availability
        self.__get_availability_score()

    def update_role(self, role: Role):
        """

        :param role:
        :return:
        """
        self._role = role

    def get_driver_availability(self, link: tuple) -> bool:
        """

        :param link:
        :return:
        """
        if len(self._availability_list) == 0:
            return False

        i, j = link
        if i not in self._availability_list or j not in self._availability_list:
            return False

        return (self._availability_list[i - 1] == 1) and (self._availability_list[j - 1] == 1)

    def can_deliver_to_link(self, link: tuple, probabilistic=True) -> bool:
        """Returns whether a driver can certainly serve a link (deterministic) or leverage probability before deciding.

        :param link:
        :param probabilistic:
        :return:
        """
        if probabilistic:
            if random.random() <= 2 / 3:
                return self.get_driver_availability(link)
        else:
            return self.get_driver_availability(link)

    def assign_route(self, route: Route):
        """

        :param route:
        :return:
        """
        self._route = route

    def __get_route(self):
        """

        :return:
        """
        return self._route

    def __get_availability_score(self):
        """

        :return:
        """
        if len(self._availability_list) == 0:
            return float('NaN')

        if self._availability_score == 0:
            self._availability_score = sum(self._availability_list)

        return self._availability_score

    @staticmethod
    def get_drivers(data):
        try:
            result = [Driver(first_name=driver.Firstname, last_name=driver.Lastname, role=driver.Role)
                      for driver in data.itertuples()]
        except Exception:
            result = []
        return result


class Drivers:
    @staticmethod
    def get_availability_score(drivers: list, reverse: bool = True) -> dict:
        """Compute availability score and sort it in decreasing order

        :return:
        """
        scores = {'D' + str(driver.id): driver.get_availability_score() for driver in drivers}
        scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=reverse))
        return scores

    @staticmethod
    def get_driver_with_shortest_distance(drivers: list, matrix: list) -> tuple:
        """Get driver with shortest distance travelled

        :param drivers:
        :param matrix:
        :return:
        """
        route_assigned = {driver.id: driver.get_route() for driver in drivers}
        driver_out = None
        shortest_distance = sys.maxsize

        for driver, route in route_assigned.items():
            route_distance = utils.route.get_route_distance(route, matrix)  # To be changed
            if shortest_distance > route_distance:
                shortest_distance = route_distance
                driver_out = driver
        return driver_out, shortest_distance
