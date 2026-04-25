class GardenError(Exception):
    """A basic error for garden problems."""
    def __init__(self, message: str = "Unknown garden error"):
        super().__init__(message)


class PlantError(GardenError):
    """For problems with plants."""
    def __init__(self, message: str = "Unknown plant error"):
        super().__init__(message)


class WaterError(GardenError):
    """For problems with watering."""
    def __init__(self, message: str = "Unknown water error"):
        super().__init__(message)


def raise_plant_error() -> None:
    """Raise a PlantError."""
    raise PlantError("The tomato plant is wilting!")


def raise_water_error() -> None:
    """Raise a WaterError."""
    raise WaterError("Not enough water in the tank!")


def test_custom_errors() -> None:
    """Demonstrate custom garden error types."""
    print("=== Custom Garden Errors Demo ===")

    print("Testing PlantError...")
    try:
        raise_plant_error()
    except PlantError as e:
        print(f"Caught PlantError: {e}")

    print("Testing WaterError...")
    try:
        raise_water_error()
    except WaterError as e:
        print(f"Caught WaterError: {e}")

    print("Testing catching all garden errors...")
    try:
        raise_plant_error()
    except GardenError as e:
        print(f"Caught GardenError: {e}")

    try:
        raise_water_error()
    except GardenError as e:
        print(f"Caught GardenError: {e}")

    print("All custom error types work correctly!")


if __name__ == "__main__":
    test_custom_errors()
