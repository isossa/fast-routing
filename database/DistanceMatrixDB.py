from utils import ReadFile


class DistanceMatrixDB:
    distance_matrix: dict = dict()

    @staticmethod
    def set_distance_matrix_from_csv(filename: str):
        DistanceMatrixDB.distance_matrix = ReadFile.read_csv(filename)
        return DistanceMatrixDB.distance_matrix

    @staticmethod
    def load(filename: str):
        """
        Load a distance matrix from a csv file.

        :param filename:
        :return:
        """
        pass

    @staticmethod
    def save():
        """
        Write the content of this distance matrix to a file
        :return:
        """


    @staticmethod
    def get_distance_matrix():
        return DistanceMatrixDB.distance_matrix

    @staticmethod
    def distance_between(l1: int, l2: int):
        return DistanceMatrixDB.distance_matrix[l1][l2]
