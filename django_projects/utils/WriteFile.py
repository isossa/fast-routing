import pickle


class WriteFile:

    @staticmethod
    def load(filename: str):
        """
        Load a distance matrix from a csv file.

        :param filename:
        :return:
        """
        with open(filename, 'rb') as input_file:
            content = pickle.load(input_file)
        return content

    @staticmethod
    def save(filename: str, obj):
        """
        Write the content of this distance matrix to a file
        :return:
        """
        with open(filename, 'wb') as output_file:
            pickle.dump(obj, output_file)
