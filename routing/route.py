import math


def get_route_demand(route: tuple, demand: dict) -> int:
    """Return total demand on this route

    :param route:
    :param demand:
    :return:
    """
    running_demand = 0
    for x in route:
        if x != 0 and not math.isnan(demand[x]):
            running_demand += demand[x]
    return running_demand


def get_route_distance(route: tuple, distance_matrix: list) -> int:
    return __get_route_statistic(route, distance_matrix)


def get_route_duration(route: tuple, duration_matrix: list) -> int:
    return __get_route_statistic(route, duration_matrix)


def __get_route_statistic(route: tuple, matrix: list) -> int:
    """Return route distance

    :param route:
    :param matrix:
    :return:
    """
    statistic = 0
    for index, value in enumerate(route):
        row = value
        if index + 1 < len(route):
            col = route[index + 1]
            if not math.isnan(matrix[row][col]):
                statistic += matrix[row][col]
    return statistic


def get_route_info(route: tuple, matrix: list, demand: dict) -> tuple[int, int, int]:
    """Return info of this route as demand and capacity

    :param route:
    :param matrix:
    :param demand:
    :return:
    """
    return get_route_demand(route, demand), get_route_distance(route, matrix), get_route_duration(route, matrix)


def get_routes(routes: dict) -> dict:
    """Return the routes solution of this savings algorithm

    :param routes:
    :return: Return the routes solution of this savings algorithm
    """
    results = {}
    for driver, route in routes.items():
        if len(route) > 0:
            temp_route = [0]
            temp_route.extend(route)
            temp_route.append(0)
            results[driver] = tuple(temp_route)
    return results


def is_interior(node: int, route: tuple) -> bool:
    """Determine if a node is interior

    :param node:
    :param route:
    :return:
    """
    return node in route[1:len(route) - 1]


def add_link(i: int, j: int, route: tuple) -> tuple:
    """Add a node to a route

    :param i:
    :param j:
    :param route:
    :return:
    """
    if len(route) == 0:
        return i, j
    else:
        route = list(route)
        location = route.index(j)
        if location == 0:
            route.insert(0, i)
        else:
            route.append(i)
    return tuple(route)


def get_total_distance(routes: dict, matrix: list):
    """Returns the combined total distance of all routes

    :param routes:
    :param matrix:
    :return:
    """
    total_distance = 0
    for driver, route in routes.items():
        total_distance += get_route_distance(route, matrix)
    return total_distance


def get_link_status(link: tuple, customers: dict) -> bool:
    """Returns True if a driver can deliver to both of these customers; otherwise False

    :param link:
    :param customers:
    :return:
    """
    if len(link) > 0:
        return node_is_active(link[0], customers) or node_is_active(link[1], customers)
    return False


def node_is_active(node: int, customers: dict) -> bool:
    """Returns whether this node has already been added to a route.

    :param node:
    :param customers:
    :return:
    """
    if node in customers.keys():
        return customers[node]
    else:
        return False


def set_node_status(node: int, nodes: dict, status: bool):
    """Set whether this customer has not been included in a route.

    :param node:
    :param nodes:
    :param status:
    :return:
    """
    nodes[node] = status
    return nodes
