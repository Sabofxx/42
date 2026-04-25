import alchemy.elements
from alchemy.elements import create_water
from alchemy.potions import healing_potion as heal
from alchemy.elements import create_earth, create_fire
from alchemy.potions import strength_potion


def main() -> None:
    print("=== Import Transmutation Mastery ===")

    print("Method 1 - Full module import:")
    print(
        "alchemy.elements.create_fire():"
        f" {alchemy.elements.create_fire()}"
    )

    print("Method 2 - Specific function import:")
    print(f"create_water(): {create_water()}")

    print("Method 3 - Aliased import:")
    print(f"heal(): {heal()}")

    print("Method 4 - Multiple imports:")
    print(f"create_earth(): {create_earth()}")
    print(f"create_fire(): {create_fire()}")
    print(
        f"strength_potion(): {strength_potion()}"
    )

    print()
    print(
        "All import transmutation"
        " methods mastered!"
    )


if __name__ == "__main__":
    main()
