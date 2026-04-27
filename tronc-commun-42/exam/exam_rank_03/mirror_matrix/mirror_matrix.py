#!/usr/bin/env python3

def mirror_matrix(matrix: list[list[int]]) -> list[list[int]]:
    return [row[::-1] for row in matrix]


def main() -> None:
    print(mirror_matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
    # [[3, 2, 1], [6, 5, 4], [9, 8, 7]]
    print(mirror_matrix([[1, 2], [3, 4], [5, 6]]))
    # [[2, 1], [4, 3], [6, 5]]
    print(mirror_matrix([[7]]))
    # [[7]]


if __name__ == "__main__":
    main()
