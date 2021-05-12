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
    def get_matrix(matrix_dict: dict, geocodes: dict) -> list:
        """Gets distance or duration matrix.

        Retrieves duration or duration matrix between pairs of a list of locations
        representing by their geocodes.

        :param matrix_dict:
        :param geocodes: A dictionary of geocodes representing locations and their indexes.
        :return: A matrix whose cells represent the travel distance/duration between pairs of
            locations.
            The unit of these numbers depends on the type (distance or duration) is specified
            by Microsoft Bing Maps Distance Matrix API.
        """
        result = [list()] * len(geocodes)
        for origin, destinations in matrix_dict.items():
            from_index = geocodes[origin]
            temp = [0] * len(geocodes)
            for pair in destinations:
                destination, value = pair
                to_index = geocodes[destination]
                temp[to_index] = value
            result[from_index] = temp
        return result

    @staticmethod
    def request_matrix(geocodes: list, api_key: str, travel_mode: str, size: int) -> tuple:
        """

        Initializes an HTTP request to Bing Maps Distance Matrix API.
        :param size: Size of matrix to request for each API call
        :param geocodes: Location geocodes specified as a list of longitude and latitude coordinates.
        :param api_key: Bing Maps Developer's API key.
        :param travel_mode: String represented the travel mode between locations.
        :return: HTTP response.
        """
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
            distance_matrix, duration_matrix, response = DistanceMatrix.__build_request_helper(geocodes=geocodes,
                                                                                               size=size, url=url,
                                                                                               params=parameters)
            if response.status_code == 200:
                DistanceMatrix.__response = response
        else:
            DistanceMatrix.__number_of_requests_saved += 1

        return distance_matrix, duration_matrix, DistanceMatrix.__response

    @staticmethod
    def __build_request_helper(geocodes: list, size: int, url, params) -> requests.Response:
        """

        :param geocodes: Location geocodes specified as a list of longitude and latitude coordinates.
        :param size:
        :param url:
        :param params:
        :return:
        """
        distance_matrix = dict()
        duration_matrix = dict()

        for i, origin in enumerate(geocodes):
            params['origins'] = '; '.join([origin])
            destinations = []
            buffet_size = 0
            for current_index in range(len(geocodes)):
                if current_index != i:
                    destinations.append(geocodes[current_index])
                    buffet_size += 1

                if buffet_size == size:
                    params['destinations'] = '; '.join(destinations)
                    response = requests.get(url, params=params)

                    if response.status_code != 200:
                        print(f"Execution stopped with HTTP code {response.status_code}")
                        return distance_matrix, duration_matrix

                    temp_distance_matrix, temp_duration_matrix = DistanceMatrix.__build_response(response, origin,
                                                                                                 destinations)
                    distance_matrix = DistanceMatrix.__update_matrix(distance_matrix, temp_distance_matrix)
                    duration_matrix = DistanceMatrix.__update_matrix(duration_matrix, temp_duration_matrix)

                    destinations = []
                    buffet_size = 0

            if len(destinations) > 0:
                params['destinations'] = '; '.join(destinations)
                response = requests.get(url, params=params)

                if response.status_code != 200:
                    print(f"Execution stopped with HTTP code {response.status_code}")
                    return distance_matrix, duration_matrix

                temp_distance_matrix, temp_duration_matrix = DistanceMatrix.__build_response(response, origin,
                                                                                             destinations)
                distance_matrix = DistanceMatrix.__update_matrix(distance_matrix, temp_distance_matrix)
                duration_matrix = DistanceMatrix.__update_matrix(duration_matrix, temp_duration_matrix)

        return distance_matrix, duration_matrix, response

    @staticmethod
    def __build_response(response, origin, destinations):
        """Creates a matrix, distance and duration between pairs of locations.

        :param response: HTTP request response. Only '200 OK' will result in matrix.
        :param origin:
        :param destinations:
        :return: Matrix of distance and duration between pairs of locations.
        """
        distance_matrix = dict()
        duration_matrix = dict()
        if response.status_code == 200:
            json_response = response.json()
            for index, r in enumerate(json_response["resourceSets"][0]['resources'][0]['results']):
                temp = distance_matrix.get(origin, list())
                temp.append((destinations[index], r['travelDistance']))
                distance_matrix[origin] = temp

                temp = duration_matrix.get(origin, list())
                temp.append((destinations[index], r['travelDuration']))
                duration_matrix[origin] = temp
        return distance_matrix, duration_matrix

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
            l1 = d1.get(key, list())
            l2 = d2.get(key, list())
            l1.extend([n for n in l2 if n not in l1])
            d1[key] = l1
        return d1
