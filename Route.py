from database.DistanceMatrixDB import DistanceMatrixDB


class Route:
    def __init__(self, route: tuple):
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

            self._distance += DistanceMatrixDB.distance_between(location1.identifier, location2.identifier)

        return self._distance

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
