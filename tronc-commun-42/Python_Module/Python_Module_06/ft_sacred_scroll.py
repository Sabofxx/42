import alchemy
import alchemy.elements


def main() -> None:
    print("=== Sacred Scroll Mastery ===")

    print("Testing direct module access:")
    print(
        "alchemy.elements.create_fire():"
        f" {alchemy.elements.create_fire()}"
    )
    print(
        "alchemy.elements.create_water():"
        f" {alchemy.elements.create_water()}"
    )
    print(
        "alchemy.elements.create_earth():"
        f" {alchemy.elements.create_earth()}"
    )
    print(
        "alchemy.elements.create_air():"
        f" {alchemy.elements.create_air()}"
    )

    print()
    print(
        "Testing package-level access"
        " (controlled by __init__.py):"
    )
    print(
        "alchemy.create_fire():"
        f" {alchemy.create_fire()}"
    )
    print(
        "alchemy.create_water():"
        f" {alchemy.create_water()}"
    )
    try:
        result = alchemy.create_earth()  # type: ignore
        print(f"alchemy.create_earth(): {result}")
    except AttributeError:
        print(
            "alchemy.create_earth():"
            " AttributeError - not exposed"
        )
    try:
        result = alchemy.create_air()  # type: ignore
        print(f"alchemy.create_air(): {result}")
    except AttributeError:
        print(
            "alchemy.create_air():"
            " AttributeError - not exposed"
        )

    print()
    print("Package metadata:")
    print(f"Version: {alchemy.__version__}")
    print(f"Author: {alchemy.__author__}")


if __name__ == "__main__":
    main()
