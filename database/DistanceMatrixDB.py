import pickle


class DistanceMatrixDB:
    distance_matrix: dict = dict()

    @staticmethod
    def load(filename: str):
        """
        Load a distance matrix from a csv file.

        :param filename:
        :return:
        """
        with open(filename, 'rb') as input_file:
            DistanceMatrixDB.distance_matrix = pickle.load(input_file)
        return DistanceMatrixDB.distance_matrix

    @staticmethod
    def save(filename: str):
        """
        Write the content of this distance matrix to a file
        :return:
        """
        with open(filename, 'wb') as output_file:
            pickle.dump(DistanceMatrixDB.distance_matrix, output_file)

    @staticmethod
    def get_distance_matrix():
        return DistanceMatrixDB.distance_matrix

    @staticmethod
    def distance_between(l1: int, l2: int):
        return DistanceMatrixDB.distance_matrix[l1][l2]
