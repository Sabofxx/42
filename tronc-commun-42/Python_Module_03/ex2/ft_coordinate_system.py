import math


def get_player_pos() -> tuple[float, float, float]:
    """Ask the user for 3D coordinates until valid input."""
    while True:
        raw = input(
            "Enter new coordinates as floats"
            " in format 'x,y,z': "
        )
        parts = raw.split(",")
        if len(parts) != 3:
            print("Invalid syntax")
            continue
        try:
            coords = []
            for p in parts:
                coords.append(float(p.strip()))
            return (coords[0], coords[1], coords[2])
        except ValueError as e:
            bad = p.strip()
            print(
                f"Error on parameter '{bad}': {e}"
            )


def distance(
    a: tuple[float, float, float],
    b: tuple[float, float, float]
) -> float:
    """Calculate Euclidean distance between two 3D points."""
    return math.sqrt(
        (b[0] - a[0]) ** 2
        + (b[1] - a[1]) ** 2
        + (b[2] - a[2]) ** 2
    )


def main() -> None:
    print("=== Game Coordinate System ===")
    print("Get a first set of coordinates")
    pos1 = get_player_pos()
    print(f"Got a first tuple: {pos1}")
    print(
        f"It includes: X={pos1[0]}, "
        f"Y={pos1[1]}, Z={pos1[2]}"
    )
    dist_center = round(
        distance(pos1, (0.0, 0.0, 0.0)), 4
    )
    print(f"Distance to center: {dist_center}")
    print("Get a second set of coordinates")
    pos2 = get_player_pos()
    dist_between = round(distance(pos1, pos2), 4)
    print(
        "Distance between the 2 sets"
        f" of coordinates: {dist_between}"
    )


if __name__ == "__main__":
    main()
