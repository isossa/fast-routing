def symmetrization(matrix):
    """Given a matrix, returned symmetrized matrix.

    If matrix is a non empty matrix, then matrix[i][j] == matrix[j][i]

    :param matrix: Non empty matrix.
    :return: Symmetrized matrix.
    """
    if matrix and len(matrix) < 2:
        return matrix

    n_row = len(matrix)
    n_col = len(matrix[0])

    if n_row != n_col:
        return matrix

    for row in range(0, n_row):
        col = row
        while col < n_col:
            local_max = max(matrix[row][col], matrix[col][row])
            matrix[row][col] = local_max
            matrix[col][row] = local_max
            col += 1
    return matrix
