import requests


class DistanceMatrix:
    """
    This class defines the mechanics for requesting a distance/duration matrix
    from a set of locations.

    This implementation relies on Microsoft Bing Maps DistanceMatrix API. A
    distance/duration can be requested by simply running the following line:

        Typical usage example:

        matrix = DistanceMatrix.get_matrix(geocodes, 'travelDistance', 'driving')

    Attributes:
        None.

    More information about the Bing Maps DistanceMatrix API can be found here:
    """

    # Defines API urls
    __api_urls = {
        "base": "https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?"
    }

    # Distance matrix between pair of locations
    __distance_matrix = list()

    # HTTP response
    __response = requests.Response()

    # Store list of last locations whose distance matrix has been requested
    __last_requested = list()

    # Count of number of unnecessary requests. These are saved!
    __number_of_requests_saved = 0

    # Total number of requests made.
    __number_of_requests_made = 0

    @staticmethod
    def request_matrix(addresses: list, api_key: str, travel_mode: str, size: int) -> tuple:
        """

        Initializes an HTTP request to Bing Maps Distance Matrix API.
        :param size: Size of matrix to request for each API call
        :param addresses: Addresses .
        :param api_key: Bing Maps Developer's API key.
        :param travel_mode: String represented the travel mode between locations.
        :return: HTTP response.
        """
        geocodes = [address.coordinates_as_string() for address in addresses]
        DistanceMatrix.__number_of_requests_made += 1
        condition1 = DistanceMatrix.__response.status_code != 200
        condition2 = not (DistanceMatrix.__identical_list(DistanceMatrix.__last_requested, geocodes))

        if condition1 or condition2:
            DistanceMatrix.__last_requested = geocodes
            parameters = {
                "origins": [],
                "destinations": [],
                "travelMode": travel_mode,
                "key": api_key
            }
            url = DistanceMatrix.__api_urls['base']
            distance_map, duration_map, response = DistanceMatrix.__build_request_helper(addresses=addresses,
                                                                                         size=size, url=url,
                                                                                         params=parameters)
            if response.status_code == 200:
                DistanceMatrix.__response = response
        else:
            DistanceMatrix.__number_of_requests_saved += 1

        return distance_map, duration_map, DistanceMatrix.__response

    @staticmethod
    def __build_request_helper(addresses: list, size: int, url, params) -> requests.Response:
        """

        :param addresses: Addresses
        :param size:
        :param url:
        :param params:
        :return:
        """
        distance_map = dict()
        duration_map = dict()

        for i, origin in enumerate(addresses):
            params['origins'] = '; '.join([origin.coordinates_as_string()])
            destinations = []
            buffet_size = 0
            for current_index in range(len(addresses)):
                if current_index != i:
                    destinations.append(addresses[current_index])
                    buffet_size += 1

                if buffet_size == size:
                    destinations_coors = [address.coordinates_as_string() for address in destinations]
                    params['destinations'] = '; '.join(destinations_coors)
                    response = requests.get(url, params=params)

                    if response.status_code != 200:
                        print(f"Execution stopped with HTTP code {response.status_code}")
                        return distance_map, duration_map

                    temp_distance_map, temp_duration_map = DistanceMatrix.__build_response(response, origin,
                                                                                           destinations)
                    distance_map = DistanceMatrix.__update_matrix(distance_map, temp_distance_map)
                    duration_map = DistanceMatrix.__update_matrix(duration_map, temp_duration_map)

                    destinations = []
                    buffet_size = 0

            if len(destinations) > 0:
                destinations_coors = [address.coordinates_as_string() for address in destinations]
                params['destinations'] = '; '.join(destinations_coors)
                response = requests.get(url, params=params)

                if response.status_code != 200:
                    print(f"Execution stopped with HTTP code {response.status_code}")
                    return distance_map, duration_map

                temp_distance_map, temp_duration_map = DistanceMatrix.__build_response(response, origin,
                                                                                       destinations)
                distance_map = DistanceMatrix.__update_matrix(distance_map, temp_distance_map)
                duration_map = DistanceMatrix.__update_matrix(duration_map, temp_duration_map)

        return distance_map, duration_map, response

    @staticmethod
    def __build_response(response, origin, destinations):
        """Creates a matrix, distance and duration between pairs of locations.

        :param response: HTTP request response. Only '200 OK' will result in matrix.
        :param origin:
        :param destinations:
        :return: Matrix of distance and duration between pairs of locations.
        """
        if response.status_code == 200:
            json_response = response.json()
            distance_map_temp = dict()
            duration_map_temp = dict()
            for index, r in enumerate(json_response["resourceSets"][0]['resources'][0]['results']):
                distance_map_temp.update({destinations[index]: r['travelDistance']})
                duration_map_temp.update({destinations[index]: r['travelDuration']})

            distance_map = {origin: distance_map_temp}
            duration_map = {origin: duration_map_temp}

        return distance_map, duration_map

    @staticmethod
    def __identical_list(list1: list, list2: list) -> bool:
        """Checks if two list are equals.

        :param list1: List of geocodes represented as string.
        :param list2: List of geocodes represented as string.
        :return: True if the list arguments contains exactly the same elements.
        """
        return len(set(list1) - set(list2)) == 0 and len(set(list2) - set(list1)) == 0

    @staticmethod
    def __update_matrix(d1, d2):
        """
        Given two dictionaries, return a dictionary containing the union of the keys in each dictionary.
        Values are the union of each dictionary key value. Duplicate values per key are not kept
        :param d1: Dictionary of the form K : V where V is a list
        :param d2: Dictionary of the form K : V where V is a list
        :return: Union of d1 and d2
        """
        for key, value in d2.items():
            l1 = d1.get(key, dict())
            l2 = d2.get(key, dict())
            l1.update({k: v for k, v in l2.items() if k not in l1})
            d1[key] = l1
        return d1
