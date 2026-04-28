def input_temperature(temp_str: str) -> int:
    """Convert a string to a temperature integer and validate range."""
    temp = int(temp_str)
    if temp > 40:
        msg = f"{temp}\u00b0C is too hot for plants (max 40\u00b0C)"
        raise ValueError(msg)
    if temp < 0:
        msg = f"{temp}\u00b0C is too cold for plants (min 0\u00b0C)"
        raise ValueError(msg)
    return temp


def test_temperature() -> None:
    """Test input_temperature with valid, invalid, and extreme inputs."""
    print("=== Garden Temperature Checker ===")

    tests = ["25", "abc", "100", "-50"]
    for temp_str in tests:
        print(f"Input data is '{temp_str}'")
        try:
            temp = input_temperature(temp_str)
            print(f"Temperature is now {temp}\u00b0C")
        except ValueError as e:
            print(f"Caught input_temperature error: {e}")

    print("All tests completed - program didn't crash!")


if __name__ == "__main__":
    test_temperature()
