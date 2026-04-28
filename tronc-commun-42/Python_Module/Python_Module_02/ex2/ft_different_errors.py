def garden_operations(operation_number: int) -> None:
    """Execute a faulty operation based on operation_number."""
    if operation_number == 0:
        int("abc")
    elif operation_number == 1:
        1 / 0
    elif operation_number == 2:
        open("/non/existent/file")
    elif operation_number == 3:
        "hello" + 42  # type: ignore
    else:
        return


def test_error_types() -> None:
    """Test different error types and demonstrate catching them."""
    print("=== Garden Error Types Demo ===")

    error_types = {
        0: "ValueError",
        1: "ZeroDivisionError",
        2: "FileNotFoundError",
        3: "TypeError",
    }

    for i in range(5):
        print(f"Testing operation {i}...")
        try:
            garden_operations(i)
            print("Operation completed successfully")
        except (ValueError, ZeroDivisionError,
                FileNotFoundError, TypeError) as e:
            error_name = error_types.get(i, "Unknown")
            print(f"Caught {error_name}: {e}")

    print("All error types tested successfully!")


if __name__ == "__main__":
    test_error_types()
