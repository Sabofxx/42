def constellation_mapper(stars: list[tuple[int, int]], size: int) -> list[str]:
    star_set = set(stars)
    grid = []
    for r in range(size):
        row = ""
        for c in range(size):
            if (r, c) in star_set:
                row += "*"
            else:
                row += "."
        grid.append(row)
    return grid


# res = constellation_mapper([(0, 0), (1, 1), (2, 2)], 3)
# print(f"excepted: ['*..', '.*.', '..*']")
# print(f"got: {res}\n")

# res = constellation_mapper([(1, 1), (0, 1), (2, 1), (1, 0), (1, 2)], 3)
# print(f"excepted: ['.*.', '***', '.*.']")
# print(f"got: {res}\n")

# res = constellation_mapper([], 2)
# print(f"excepted: ['..', '..']")
# print(f"got: {res}\n")

# res = constellation_mapper([(0, 0), (0, 0), (1, 1)], 2)
# print(f"excepted: ['*.', '.*']")
# print(f"got: {res}\n")

# res = constellation_mapper([(0, 0), (5, 5)], 3)
# print(f"excepted: ['*..', '...', '...']")
# print(f"got: {res}\n")

# res = constellation_mapper([(1, 0), (1, 1), (1, 2)], 3)
# print(f"excepted: ['...', '***', '...']")
# print(f"got: {res}\n")
