import itertools
import random
import sys

from .utils.route import get_route_demand
from .utils.route import get_route_duration, node_is_active, add_link, set_node_status, get_link_status, is_interior, \
    get_route_distance
from .utils.savingsutils import get_maximum_savings


def valid_assignment(route: tuple, demand: dict):
    pass


def update_route(link: tuple, route: tuple, capacity: int, demand: dict, duration_matrix: dict, locations: dict) -> tuple:
    """Update routes

    :param link:
    :param route:
    :param capacity:
    :param demand:
    :param locations:
    :return:
    """
    if len(route) == 0:
        if node_is_active(link[0], locations) and node_is_active(link[1], locations):
            route = add_link(link[0], link[1], route)
            set_node_status(link[0], locations, False)
            set_node_status(link[1], locations, False)
    else:
        i, j = link
        # Exactly one of i or j has been already included and that point
        # is not interior to this route
        if ((i in route) ^ (j in route)) and get_link_status(link, locations):
            if i in route and not is_interior(i, route) and node_is_active(j, locations):
                expected_demand = get_route_demand(route, demand) + demand[j]
                expected_duration = get_route_duration(route, duration_matrix) + 10
                if expected_demand <= capacity:
                    route = add_link(j, i, route)
                    set_node_status(i, locations, False)
                    set_node_status(j, locations, False)
                    print('EXPECTED DEMAND', expected_demand)
                    print('MAX CAPACITY', capacity)
                    print('ROUTE', route)
            elif j in route and not is_interior(j, route) and node_is_active(i, locations):
                expected_demand = get_route_demand(route, demand) + demand[i]
                if expected_demand <= capacity:
                    route = add_link(i, j, route)
                    set_node_status(i, locations, False)
                    set_node_status(j, locations, False)
                    print('EXPECTED DEMAND', expected_demand)
                    print('MAX CAPACITY', capacity)
                    print('ROUTE', route)

    return route


def can_deliver_to_link(driver: str, link: tuple, availability_map: dict, probabilistic=True) -> bool:
    """Returns whether a driver can certainly serve a link (deterministic) or leverage probability before deciding.

    :param driver:
    :param link:
    :param availability_map:
    :param probabilistic:
    :return:
    """
    if probabilistic:
        if random.random() <= 2 / 3:
            return get_driver_availability(driver, link, availability_map)
    else:
        return get_driver_availability(driver, link, availability_map)


def get_driver_availability(driver: str, link: tuple, availability_map: dict) -> bool:
    if driver in availability_map.keys():
        availability = availability_map[driver]
        i, j = link
        return (availability[i] == 1) and (availability[j] == 1)
    else:
        return False


def get_availability_score(availability: dict) -> dict:
    """Compute availability score and sort it in decreasing order

    :param availability:
    :return:
    """
    scores = {}
    for driver in availability.keys():
        driver_availability = availability[driver]
        scores[driver] = sum(driver_availability.values())

    scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
    return scores


def get_availability_map(availability: dict) -> dict:
    """Compute availability map and sort it in decreasing order

    :param availability:
    :return:
    """
    availability_map = get_availability_score(availability)

    for driver in availability_map.keys():
        index = int(driver[1:]) - 1
        availability_map[driver] = availability[index]
    return availability_map


def get_driver_with_shortest_distance(route_assigned: dict, matrix: list) -> tuple:
    """Get driver with shortest distance travelled

    :param route_assigned:
    :param matrix:
    :return:
    """
    shortest_distance = sys.maxsize
    driver_out = None
    for driver, route in route_assigned.items():
        route_distance = get_route_distance(route, matrix)
        if shortest_distance > route_distance:
            shortest_distance = route_distance
            driver_out = driver
    return driver_out, shortest_distance


def run_restricted_assignment(sorted_savings: dict, capacity: int, demand: dict, customers: dict,
                              availability_map: dict, duration_matrix: dict):
    """Assign routes to drivers under constraints

    :param sorted_savings:
    :param capacity:
    :param demand:
    :param customers:
    :param availability_map:
    :return:
    """
    routes_assignment = {driver: tuple() for driver in availability_map}

    for link in sorted_savings.keys():
        for driver in routes_assignment.keys():
            route = routes_assignment[driver]
            if can_deliver_to_link(driver, link, availability_map, False) and get_link_status(link, customers):
                previous_route = route
                route = update_route(link, route, capacity, demand, duration_matrix, customers)
                if route != previous_route:
                    routes_assignment[driver] = route
                    break
    return routes_assignment, customers


def insert_on_margin(routes: dict, sorted_savings: dict, capacity: int, demand: dict, customers: dict,
                     marginal_capacity: int, duration_matrix: dict) -> tuple:
    """Insert customers to existing routes if doing this does not exceed a certain THRESHOLD

    :param routes:
    :param sorted_savings:
    :param capacity:
    :param demand:
    :param customers:
    :param marginal_capacity:
    :return:
    """
    remaining_locations = [node for node in customers if customers[node]]

    for location in remaining_locations:
        driver, link, _ = get_maximum_savings(routes, [location], sorted_savings)
        route = routes[driver]
        previous_route = route
        expected_capacity = get_route_demand(route, demand) + demand[location]
        relaxed_capacity = capacity + marginal_capacity
        # print(f'FLAG {driver}, {location}')
        route = update_route(link, route, relaxed_capacity, demand, duration_matrix, customers)
        if previous_route != route:
            routes[driver] = route
            print('FROM INSERT ON MARGIN')
            break

    remaining_locations = [node for node in customers if customers[node]]
    return routes, remaining_locations, customers


def insert_last_customer(routes: dict, savings: dict, capacity: int, demand: dict, duration_matrix: dict, customers: dict):
    """Insert last customer to exiting routes, whenever that is possible

    :param routes:
    :param savings:
    :param capacity:
    :param demand:
    :param customers:
    :return:
    """
    last_to_insert = [location for location, status in customers.items() if status]
    local_savings = {}
    for driver, route in routes.items():
        if len(route) > 0:
            outer_customers = [route[0], route[len(route) - 1]]
            links = itertools.product(outer_customers, last_to_insert)
            links = [tuple(sorted(link)) for link in links]
            links.sort(key=lambda link: link[0])
            local_savings.update({link: savings[link] for link in links})
    local_savings = dict(sorted(local_savings.items(), key=lambda item: item[1], reverse=True))

    index = 0
    links = list(local_savings.keys())
    non_inserted = True
    while non_inserted and index < len(links):
        link = links[index]
        index += 1
        for driver in routes.keys():
            route = routes[driver]
            previous_route = route
            route = update_route(link, route, capacity, demand, customers)
            if previous_route != route:
                routes[driver] = route
                print('FROM INSERT LAST CUSTOMER')
                non_inserted = False
                break
    return routes


def run_feasible_assignment(sorted_savings: dict, capacity: int, demand: dict, customers: dict,
                            availability_map: dict, duration_matrix: dict, marginal_capacity: int) -> tuple:
    """Build routes assuming

    :param sorted_savings:
    :param capacity:
    :param demand:
    :param customers:
    :param availability_map:
    :param marginal_capacity:
    :duration_matrix:
    :return:

    """
    locations = {customer: assigned for customer, assigned in customers.items() if not assigned}
    all_routes = {}
    iteration_counter = 1
    routes_assignment = {}
    while len(locations) > 0 and iteration_counter < 10:
        if len(locations) == len(customers):
            routes_assignment, locations = run_restricted_assignment(sorted_savings, capacity, demand,
                                                                     locations, availability_map, duration_matrix)
        elif len(locations) > 1:
            routes_assignment, remaining_locations, locations = insert_on_margin(routes_assignment, sorted_savings,
                                                                                 capacity, demand, locations,
                                                                                 marginal_capacity, duration_matrix)
        elif len(locations) == 1:
            d = next(iter(locations.values()))
            print('FROM RUN FEASIBLE ASSIGNMENT - BEFORE IF')
            if capacity - d == 1:
                print('FROM RUN FEASIBLE ASSIGNMENT - INSIDE IF')
                routes_assignment = insert_last_customer(routes_assignment, sorted_savings,
                                                         capacity + marginal_capacity,
                                                         demand, duration_matrix, locations)

        customers.update(locations)
        locations = {customer: status for customer, status in customers.items() if status}
        all_routes['Iteration ' + str(iteration_counter)] = routes_assignment
        iteration_counter += 1

    all_assigned = (len(locations) == 0)
    return routes_assignment, all_routes, customers, all_assigned


def build_routes(sorted_savings: dict, capacity: int, demand: dict, customers: dict, availability_map: dict, duration_matrix: dict,
                 marginal_capacity: int) -> tuple:
    iteration = 0
    all_assigned = False
    all_routes = {}
    routes_assignment = {}

    while not all_assigned and iteration <= 10:
        dummy_drivers = {}
        for driver, availability in availability_map.items():
            dummy_drivers[str(driver) + '_' + str(iteration)] = availability

        iteration += 1

        customers_to_assign = {customer: assigned for customer, assigned in customers.items() if not assigned}

        print("\nCustomer to assigned - BUILD ROUTES - Iteration ", iteration, customers_to_assign, "\n\n\n")

        routes_assignment_new, all_routes_new, customers_new, all_assigned = \
            run_feasible_assignment(sorted_savings, capacity, demand, customers_to_assign, dummy_drivers,
                                    duration_matrix, marginal_capacity)

        routes_assignment.update(routes_assignment_new)
        all_routes.update(all_routes_new)
        customers.update(customers_new)

    return routes_assignment, all_routes, customers, all_assigned


def assign_routes(sorted_savings: dict, capacity: int, demand: dict, customers: dict, availability_map: dict,
                  duration_matrix: dict, marginal_capacity: int = 0) -> tuple:
    """Build routes

    :param sorted_savings:
    :param capacity:
    :param demand:
    :param customers:
    :param availability_map:
    :param duration_matrix:
    :param marginal_capacity:
    :return:

    """

    routes_assignment, all_routes, customers, all_assigned = \
        build_routes(sorted_savings, capacity, demand, customers, availability_map, duration_matrix, marginal_capacity)

    return routes_assignment, all_routes, customers, all_assigned


def satisfy_capacity_constraint(route: list, capacity: int, demand: dict) -> bool:
    """Check if all constraints are satisfied

    :param route:
    :param capacity:
    :param demand:
    :return:
    """
    return get_route_demand(route=route, demand=demand) <= capacity
