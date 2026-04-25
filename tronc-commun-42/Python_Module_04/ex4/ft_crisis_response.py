import os


def crisis_handler(
    filename: str, routine: bool = False
) -> None:
    """Handle archive access with crisis response."""
    if routine:
        label = "ROUTINE ACCESS"
    else:
        label = "CRISIS ALERT"
    print(
        f"{label}: Attempting access"
        f" to '{filename}'..."
    )
    try:
        with open(filename, "r") as f:
            content = f.read().strip()
        print(
            f"SUCCESS: Archive recovered"
            f" - ``{content}''"
        )
        print("STATUS: Normal operations resumed")
    except FileNotFoundError:
        print(
            "RESPONSE: Archive not found"
            " in storage matrix"
        )
        print("STATUS: Crisis handled, system stable")
    except PermissionError:
        print(
            "RESPONSE: Security protocols"
            " deny access"
        )
        print(
            "STATUS: Crisis handled,"
            " security maintained"
        )
    except Exception as e:
        print(f"RESPONSE: Unexpected anomaly - {e}")
        print("STATUS: Crisis contained")


def main() -> None:
    print("=== CYBER ARCHIVES - CRISIS RESPONSE SYSTEM ===")

    crisis_handler("lost_archive.txt")
    print()

    restricted = "classified_vault.txt"
    with open(restricted, "w") as f:
        f.write("classified")
    os.chmod(restricted, 0o000)
    crisis_handler(restricted)
    os.chmod(restricted, 0o644)
    os.remove(restricted)
    print()

    crisis_handler("standard_archive.txt", routine=True)
    print()

    print(
        "All crisis scenarios handled"
        " successfully. Archives secure."
    )


if __name__ == "__main__":
    main()
