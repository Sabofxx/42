#!/usr/bin/env python3

def mirror_matrix(matrix: list[list[int]]) -> list[list[int]]:
    return [row[::-1] for row in matrix]


def main() -> None:
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    print(mirror_matrix(matrix))


if __name__ == "__main__":
    main()
