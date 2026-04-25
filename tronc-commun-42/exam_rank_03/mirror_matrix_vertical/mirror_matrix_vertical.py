#!/usr/bin/env python3

def mirror_matrix_vertical(matrix: list[list[int]]) -> list[list[int]]:
    return matrix[::-1]


def main() -> None:
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    print(mirror_matrix_vertical(matrix))


if __name__ == "__main__":
    main()
