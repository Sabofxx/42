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


print(constellation_mapper([], 2))
