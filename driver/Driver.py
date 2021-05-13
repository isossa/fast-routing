import random

from driver.Role import Role
from routing.Route import Route


class Driver:
    def __init__(self, first_name: str, last_name: str, identifier: str, role: Role):
        """

        :param first_name:
        :param last_name:
        :param identifier:
        :param role:
        """
        self._first_name: str = first_name
        self._last_name: str = last_name
        self._id: str = identifier
        self._availability_list: list = list()
        self._availability_score: int = 0
        self._route: Route = Route(route=tuple())
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
    def id(self):
        """

        :return:
        """
        return self._id

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
