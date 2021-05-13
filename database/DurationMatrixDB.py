import pickle

from utils.WriteFile import WriteFile


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
