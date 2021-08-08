from .utils.WriteFile import WriteFile


class DistanceMatrixDB:
    distance_matrix: dict = dict()

    @staticmethod
    def load(filename: str):
        """
        Load a distance matrix from a file.

        :param filename:
        :return:
        """
        DistanceMatrixDB.distance_matrix = WriteFile.load(filename)
        return DistanceMatrixDB.distance_matrix

    @staticmethod
    def save(filename: str):
        """
        Write the content of this distance matrix to a file
        :return:
        """
        WriteFile.save(filename, DistanceMatrixDB.distance_matrix)

    @staticmethod
    def get_distance_matrix():
        return DistanceMatrixDB.distance_matrix

    @staticmethod
    def distance_between(add1, add2):
        return DistanceMatrixDB.distance_matrix[add1.coordinates_as_string()][add2.coordinates_as_string()]


class DurationMatrixDB:
    duration_matrix: dict = dict()

    @staticmethod
    def load(filename: str):
        """
        Load a distance matrix from a file.

        :param filename:
        :return:
        """
        DurationMatrixDB.duration_matrix = WriteFile.load(filename)
        return DurationMatrixDB.duration_matrix

    @staticmethod
    def save(filename: str):
        """
        Write the content of this distance matrix to a file
        :return:
        """
        WriteFile.save(filename, DurationMatrixDB.duration_matrix)

    @staticmethod
    def get_duration_matrix():
        return DurationMatrixDB.duration_matrix

    @staticmethod
    def duration_between(add1, add2):
        return DurationMatrixDB.duration_matrix[add1.coordinates_as_string()][add2.coordinates_as_string()]
