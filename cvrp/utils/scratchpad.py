import os
from multiprocessing import Pool


def square(x):
    return x * x


if __name__ == '__main__':
    array = list(range(10))
    with Pool(5) as p:
        print(p.map(square, array))

    print(os.cpu_count() - 1)
