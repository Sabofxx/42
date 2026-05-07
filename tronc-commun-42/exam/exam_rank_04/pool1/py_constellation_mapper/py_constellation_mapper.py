def constellation_mapper(stars: list[tuple[int, int]], size: int) -> list[str]:
    grid = []
    for x in range(size):
        line = ""
        for y in range(size):
            if (x, y) in stars:
                line += "*"
            else:
                line += "."
        grid.append(line)
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

def constellation_mapper(stars: list[tuple[int, int]], size: int) -> list[str]:
    grid = []
    for x in range(size):
        result = ""
        for y in range(size):
            if (x,y) in stars:
                result += "*"
            else:
                result += "."
        grid.append(result)
    return grid
