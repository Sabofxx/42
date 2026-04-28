def input_temperature(temp_str: str) -> int:
    """Convert a string to a temperature integer."""
    return int(temp_str)


def test_temperature() -> None:
    """Test the input_temperature function with valid and invalid inputs."""
    print("=== Garden Temperature ===")

    temp_str = "25"
    print(f"Input data is '{temp_str}'")
    try:
        temp = input_temperature(temp_str)
        print(f"Temperature is now {temp}°C")
    except ValueError as e:
        print(f"Caught input_temperature error: {e}")

    temp_str = "abc"
    print(f"Input data is '{temp_str}'")
    try:
        temp = input_temperature(temp_str)
        print(f"Temperature is now {temp}°C")
    except ValueError as e:
        print(f"Caught input_temperature error: {e}")

    print("All tests completed - program didn't crash!")


if __name__ == "__main__":
    test_temperature()
