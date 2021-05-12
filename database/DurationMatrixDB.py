import pickle


class DurationMatrixDB:
    duration_matrix: dict = dict()

    @staticmethod
    def load(filename: str):
        """
        Load a distance matrix from a csv file.

        :param filename:
        :return:
        """
        with open(filename, 'rb') as input_file:
            DurationMatrixDB.duration_matrix = pickle.load(input_file)
        return DurationMatrixDB.duration_matrix

    @staticmethod
    def save(filename: str):
        """
        Write the content of this distance matrix to a file
        :return:
        """
        with open(filename, 'wb') as output_file:
            pickle.dump(DurationMatrixDB.duration_matrix, output_file)

    @staticmethod
    def get_duration_matrix():
        return DurationMatrixDB.duration_matrix

    @staticmethod
    def duration_between(l1: int, l2: int):
        return DurationMatrixDB.duration_matrix[l1][l2]
