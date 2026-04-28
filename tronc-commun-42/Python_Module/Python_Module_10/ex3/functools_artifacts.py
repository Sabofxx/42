import functools
import operator
from collections.abc import Callable
from typing import Any


def spell_reducer(
    spells: list[int], operation: str,
) -> int:
    """Reduce spell powers using operations."""
    if not spells:
        return 0
    ops: dict[str, Callable] = {
        'add': operator.add,
        'multiply': operator.mul,
        'max': max,
        'min': min,
    }
    if operation not in ops:
        raise ValueError(
            f"Unknown operation: {operation}"
        )
    return functools.reduce(
        ops[operation], spells
    )


def partial_enchanter(
    base_enchantment: Callable,
) -> dict[str, Callable]:
    """Create partial applications."""
    return {
        'fire': functools.partial(
            base_enchantment, 50, 'fire',
        ),
        'ice': functools.partial(
            base_enchantment, 50, 'ice',
        ),
        'lightning': functools.partial(
            base_enchantment, 50, 'lightning',
        ),
    }


@functools.lru_cache(maxsize=None)
def memoized_fibonacci(n: int) -> int:
    """Cached fibonacci calculation."""
    if n <= 1:
        return n
    return (
        memoized_fibonacci(n - 1)
        + memoized_fibonacci(n - 2)
    )


def spell_dispatcher() -> Callable[[Any], str]:
    """Create single dispatch spell system."""
    @functools.singledispatch
    def cast(spell: object) -> str:
        return "Unknown spell type"

    @cast.register(int)
    def cast_int(spell: int) -> str:
        return f"Damage spell: {spell} damage"

    @cast.register(str)
    def cast_str(spell: str) -> str:
        return f"Enchantment: {spell}"

    @cast.register(list)
    def cast_list(
        spell: list[Any],
    ) -> str:
        return f"Multi-cast: {len(spell)} spells"

    _ = (cast_int, cast_str, cast_list)

    return cast  # type: ignore[return-value]


def main() -> None:
    """Demonstrate functools mastery."""
    print("Testing spell reducer...")
    spells = [10, 20, 30, 40]
    print(f"Sum: {spell_reducer(spells, 'add')}")
    print(
        "Product:"
        f" {spell_reducer(spells, 'multiply')}"
    )
    print(f"Max: {spell_reducer(spells, 'max')}")

    print("Testing partial enchanter...")

    def enchant(
        power: int, element: str, target: str,
    ) -> str:
        return (
            f"{element} enchantment"
            f" ({power} power) on {target}"
        )

    enchants = partial_enchanter(enchant)
    print(enchants['fire']('Dragon'))
    print(enchants['ice']('Goblin'))

    print("Testing memoized fibonacci...")
    print(f"Fib(0): {memoized_fibonacci(0)}")
    print(f"Fib(1): {memoized_fibonacci(1)}")
    print(f"Fib(10): {memoized_fibonacci(10)}")
    print(f"Fib(15): {memoized_fibonacci(15)}")

    print("Testing spell dispatcher...")
    dispatch = spell_dispatcher()
    print(dispatch(42))
    print(dispatch("fireball"))
    print(dispatch([1, 2, 3]))
    print(dispatch(3.14))


if __name__ == "__main__":
    main()
