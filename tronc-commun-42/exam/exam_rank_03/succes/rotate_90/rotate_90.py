#!/usr/bin/env python3

def rotate_90(matrix: list[list[int]]) -> list[list[int]]:
    n = len(matrix)
    return [[matrix[n - 1 - j][i] for j in range(n)] for i in range(n)]


def main() -> None:
    print(rotate_90([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
    # [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
    print(rotate_90([[1, 2], [3, 4]]))
    # [[3, 1], [4, 2]]
    print(rotate_90([[1]]))
    # [[1]]


if __name__ == "__main__":
    main()
