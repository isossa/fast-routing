from ..utils.WriteFile import WriteFile


class DistanceMatrixDB:
    distance_matrix: dict = dict()

    @staticmethod
    def load(filename: str):
        """
        Load a distance matrix from a csv file.

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
    def distance_between(l1: int, l2: int):
        return DistanceMatrixDB.distance_matrix[l1][l2]


class DurationMatrixDB:
    duration_matrix: dict = dict()

    @staticmethod
    def load(filename: str):
        """
        Load a distance matrix from a csv file.

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
    def duration_between(l1: int, l2: int):
        return DurationMatrixDB.duration_matrix[l1][l2]
