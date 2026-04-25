from alchemy.grimoire import (
    validate_ingredients,
    record_spell,
)


def main() -> None:
    print("=== Circular Curse Breaking ===")

    print("Testing ingredient validation:")
    print(
        'validate_ingredients("fire air"):'
        f" {validate_ingredients('fire air')}"
    )
    print(
        'validate_ingredients("dragon scales"):'
        f" {validate_ingredients('dragon scales')}"
    )

    print()
    print(
        "Testing spell recording with validation:"
    )
    print(
        'record_spell("Fireball", "fire air"):'
        f" {record_spell('Fireball', 'fire air')}"
    )
    print(
        'record_spell("Dark Magic", "shadow"):'
        f" {record_spell('Dark Magic', 'shadow')}"
    )

    print()
    print("Testing late import technique:")
    print(
        'record_spell("Lightning", "air"):'
        f" {record_spell('Lightning', 'air')}"
    )
    print(
        "Circular dependency curse"
        " avoided using late imports!"
    )

    print()
    print("All spells processed safely!")


if __name__ == "__main__":
    main()
