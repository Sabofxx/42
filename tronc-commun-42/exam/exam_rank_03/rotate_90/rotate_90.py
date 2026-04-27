#!/usr/bin/env python3

def rotate_90(matrix: list[list[int]]) -> list[list[int]]:
    n = len(matrix)
    return [[matrix[n - 1 - j][i] for j in range(n)] for i in range(n)]


def main() -> None:
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    print(rotate_90(matrix))


if __name__ == "__main__":
    main()
