import sys

from utils.route import get_route_distance


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

        shortest_distance = sys.maxsize
        for driver, route in route_assigned.items():
            route_distance = get_route_distance(route, matrix)
            if shortest_distance > route_distance:
                shortest_distance = route_distance
                driver_out = driver
        return driver_out, shortest_distance

