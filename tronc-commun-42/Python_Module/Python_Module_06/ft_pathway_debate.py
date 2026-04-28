import alchemy.transmutation
from alchemy.transmutation.basic import (
    lead_to_gold,
    stone_to_gem,
)
from alchemy.transmutation.advanced import (
    philosophers_stone,
    elixir_of_life,
)


def main() -> None:
    print("=== Pathway Debate Mastery ===")

    print("Testing Absolute Imports (from basic.py):")
    print(f"lead_to_gold(): {lead_to_gold()}")
    print(f"stone_to_gem(): {stone_to_gem()}")

    print()
    print(
        "Testing Relative Imports"
        " (from advanced.py):"
    )
    print(
        "philosophers_stone():"
        f" {philosophers_stone()}"
    )
    print(
        f"elixir_of_life(): {elixir_of_life()}"
    )

    print()
    print("Testing Package Access:")
    print(
        "alchemy.transmutation.lead_to_gold():"
        f" {alchemy.transmutation.lead_to_gold()}"
    )
    print(
        "alchemy.transmutation"
        ".philosophers_stone():"
        f" {alchemy.transmutation.philosophers_stone()}"
    )

    print()
    print(
        "Both pathways work!"
        " Absolute: clear, Relative: concise"
    )


if __name__ == "__main__":
    main()
