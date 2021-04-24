from routing.route import get_route_demand


def satisfy_capacity_constraint(route: list, capacity: int, demand: dict) -> bool:
    """Check if all constraints are satisfied

    :param route:
    :param capacity:
    :param demand:
    :return:
    """
    return get_route_demand(route=route, demand=demand) <= capacity
