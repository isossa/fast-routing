import itertools
import sys

from ..base.common import Address
from .WriteFile import WriteFile


def get_maximum_savings(routes: dict, non_inserted: list, savings: dict) -> tuple:
    """Returns driver with max savings

    :param routes:
    :param non_inserted:
    :param savings:
    :return:
    """
    max_savings = -sys.maxsize
    max_driver = None
    max_link = None
    for driver, route in routes.items():
        if len(route) > 0:
            outer_customers = [route[0], route[len(route) - 1]]
            links = itertools.product(outer_customers, non_inserted)
            links = [tuple(sorted(link)) for link in links]
            links.sort(key=lambda link: link[0])
            print(links)
            for link in links:
                if savings[link] > max_savings:
                    max_savings = savings[link]
                    max_driver = driver
                    max_link = link
    return max_driver, max_link, max_savings


class SavingsDB:
    savings_map: dict = dict()
    sorted_savings_map: dict = dict()

    @staticmethod
    def compute_saving_matrix(distance_map: dict, depot: Address) -> dict:
        """ Matrix of locations. Compute savings matrix

        :param depot:
        :param distance_map:
        :return:
        """
        for origin in distance_map.keys():
            if origin != depot:
                temp = dict()
                for destination in distance_map[origin]:
                    if destination != depot:
                        value = distance_map[origin][depot] + distance_map[depot][destination]
                        value -= distance_map[origin][destination]
                        temp.update({destination: value})
                SavingsDB.savings_map[origin] = temp

        return SavingsDB.savings_map

    @staticmethod
    def get_sorted_map():
        """ Rank savings matrix in descending order of magnitude

        :return:
        """
        if len(SavingsDB.sorted_savings_map) == 0:
            for origin in SavingsDB.savings_map.keys():
                for destination, savings in SavingsDB.savings_map[origin].items():
                    SavingsDB.sorted_savings_map[(origin, destination)] = savings
            SavingsDB.sorted_savings_map = dict(sorted(SavingsDB.sorted_savings_map.items(), key=lambda item: item[1],
                                                       reverse=True))
        return SavingsDB.sorted_savings_map

    @staticmethod
    def save_map(filename: str):
        WriteFile.save(filename, SavingsDB.savings_map)

    @staticmethod
    def save_sorted_map(filename: str):
        WriteFile.save(filename, SavingsDB.sorted_savings_map)

    @staticmethod
    def load_sorted_map(filename):
        SavingsDB.sorted_savings_map = WriteFile.load(filename)
        return SavingsDB.sorted_savings_map

    @staticmethod
    def load_map(filename: str):
        SavingsDB.savings_map = WriteFile.load(filename)
        return SavingsDB.savings_map
