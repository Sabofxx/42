from collections.abc import Callable


def spell_combiner(
    spell1: Callable, spell2: Callable,
) -> Callable:
    """Combine two spells into one."""
    def combined(
        target: str, power: int,
    ) -> tuple[str, str]:
        return (
            spell1(target, power),
            spell2(target, power),
        )
    return combined


def power_amplifier(
    base_spell: Callable, multiplier: int,
) -> Callable:
    """Amplify spell power by a multiplier."""
    def amplified(
        target: str, power: int,
    ) -> str:
        return base_spell(
            target, power * multiplier
        )
    return amplified


def conditional_caster(
    condition: Callable, spell: Callable,
) -> Callable:
    """Cast spell only if condition is met."""
    def caster(target: str, power: int) -> str:
        if condition(target, power):
            return spell(target, power)
        return "Spell fizzled"
    return caster


def spell_sequence(
    spells: list[Callable],
) -> Callable:
    """Create a sequence of spells."""
    def sequence(
        target: str, power: int,
    ) -> list[str]:
        return [
            spell(target, power)
            for spell in spells
        ]
    return sequence


def main() -> None:
    """Demonstrate higher-order functions."""
    def fireball(target: str, power: int) -> str:
        return f"Fireball hits {target}"

    def heal(target: str, power: int) -> str:
        return f"Heals {target}"

    def damage(target: str, power: int) -> str:
        return f"{power}"

    print("Testing spell combiner...")
    combined = spell_combiner(fireball, heal)
    result = combined("Dragon", 50)
    print(
        "Combined spell result:"
        f" {result[0]}, {result[1]}"
    )

    print("Testing power amplifier...")
    mega = power_amplifier(damage, 3)
    print(
        f"Original: {damage('target', 10)},"
        f" Amplified: {mega('target', 10)}"
    )

    print("Testing conditional caster...")
    guarded = conditional_caster(
        lambda t, p: p >= 50, fireball,
    )
    print(guarded("Dragon", 100))
    print(guarded("Dragon", 10))

    print("Testing spell sequence...")
    seq = spell_sequence([fireball, heal])
    results = seq("Dragon", 50)
    for r in results:
        print(f"  {r}")


if __name__ == "__main__":
    main()
