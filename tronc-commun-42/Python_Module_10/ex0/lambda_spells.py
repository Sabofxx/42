def artifact_sorter(
    artifacts: list[dict],
) -> list[dict]:
    """Sort artifacts by power level descending."""
    return sorted(
        artifacts,
        key=lambda a: a['power'],
        reverse=True,
    )


def power_filter(
    mages: list[dict], min_power: int,
) -> list[dict]:
    """Filter mages by minimum power level."""
    return list(filter(
        lambda m: m['power'] >= min_power, mages
    ))


def spell_transformer(
    spells: list[str],
) -> list[str]:
    """Transform spell names with markers."""
    return list(map(lambda s: f"* {s} *", spells))


def mage_stats(mages: list[dict]) -> dict:
    """Calculate mage power statistics."""
    powers = list(map(lambda m: m['power'], mages))
    return {
        'max_power': max(powers),
        'min_power': min(powers),
        'avg_power': round(
            sum(powers) / len(powers), 2
        ),
    }


def main() -> None:
    """Demonstrate lambda spell functions."""
    artifacts = [
        {'name': 'Crystal Orb', 'power': 85,
         'type': 'orb'},
        {'name': 'Fire Staff', 'power': 92,
         'type': 'staff'},
        {'name': 'Ice Dagger', 'power': 67,
         'type': 'weapon'},
    ]

    print("Testing artifact sorter...")
    sorted_arts = artifact_sorter(artifacts)
    first = sorted_arts[0]
    second = sorted_arts[1]
    print(
        f"{first['name']} ({first['power']} power)"
        f" comes before"
        f" {second['name']}"
        f" ({second['power']} power)"
    )

    spells = ['fireball', 'heal', 'shield']
    print("Testing spell transformer...")
    transformed = spell_transformer(spells)
    print(" ".join(transformed))

    mages = [
        {'name': 'Merlin', 'power': 95,
         'element': 'fire'},
        {'name': 'Gandalf', 'power': 88,
         'element': 'light'},
        {'name': 'Novice', 'power': 30,
         'element': 'earth'},
    ]

    print("Testing power filter...")
    strong = power_filter(mages, 50)
    for m in strong:
        print(
            f"  {m['name']}"
            f" (power: {m['power']})"
        )

    print("Testing mage stats...")
    stats = mage_stats(mages)
    print(f"  Max: {stats['max_power']}")
    print(f"  Min: {stats['min_power']}")
    print(f"  Avg: {stats['avg_power']}")


if __name__ == "__main__":
    main()
