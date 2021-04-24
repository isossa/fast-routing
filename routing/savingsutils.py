import itertools
import sys


def compute_saving_matrix(matrix: list) -> list:
    """Compute savings matrix

    :param matrix:
    :return:
    """
    locations = len(matrix)
    return [[matrix[i][0] + matrix[0][j] - matrix[i][j] if i != j else float('NaN') for j in range(locations)]
            for i in range(locations)]


def get_max_sorted_savings(savings: list) -> dict:
    """Rank savings matrix in descending order of magnitude

    :param savings:
    :return:
    """
    ordering = {}
    for from_index in range(1, len(savings)):
        saving = savings[from_index]
        for to_index in range(from_index + 1, len(savings)):
            ordering[(from_index, to_index)] = saving[to_index]
    ordering = dict(sorted(ordering.items(), key=lambda item: item[1], reverse=True))
    return ordering


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
            for link in links:
                if savings[link] > max_savings:
                    max_savings = savings[link]
                    max_driver = driver
                    max_link = link
    return max_driver, max_link, max_savings
