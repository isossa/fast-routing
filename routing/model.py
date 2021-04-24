from routing.SavingsAlgorithm import run_feasible_assignment


def solver(sorted_savings: dict, capacity: int, demand: dict, customers: dict, availability_map: dict,
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

        customers_to_assign = {customer: status for customer, status in customers.items() if status}

        routes_assignment_new, all_routes_new, customers_new, all_assigned = \
            run_feasible_assignment(sorted_savings, capacity, demand, customers_to_assign, dummy_drivers,
                                    marginal_capacity)

        routes_assignment.update(routes_assignment_new)
        all_routes.update(all_routes_new)
        customers.update(customers_new)

    return routes_assignment, all_routes, customers, all_assigned


def build_routes(sorted_savings: dict, capacity: int, distance_matrix: list, demand: dict, customers: dict,
                 availability_map: dict, marginal_capacity: int) -> tuple:
    """Build routes

    :param sorted_savings:
    :param capacity:
    :param distance_matrix:
    :param demand:
    :param customers:
    :param availability_map:
    :param marginal_capacity:
    :return:
    """
    f = open('log.txt', 'a')
    all_routes = {}

    routes_assignment, all_routes, customers, all_assigned = \
        solver(sorted_savings, capacity, demand, customers, availability_map, marginal_capacity)

    f.write(f'\n\nFinal state {routes_assignment}\n\n')

    print(f'\nSolver status: ',
          'All locations have been assigned' if all_assigned else 'Some locations are not assigned.')
    f.close()
    return routes_assignment, all_assigned
