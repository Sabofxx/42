import random


ALL_ACHIEVEMENTS = [
    "Master Explorer", "Boss Slayer", "Speed Runner",
    "Collector Supreme", "Crafting Genius", "Untouchable",
    "World Savior", "First Steps", "Hidden Path Finder",
    "Strategist", "Survivor", "Treasure Hunter",
    "Sharp Mind", "Unstoppable",
]


def gen_player_achievements() -> set[str]:
    """Randomly assign a set of achievements to a player."""
    count = random.randint(4, len(ALL_ACHIEVEMENTS))
    return set(random.sample(ALL_ACHIEVEMENTS, count))


def main() -> None:
    print("=== Achievement Tracker System ===")
    names = ["Alice", "Bob", "Charlie", "Dylan"]
    players: dict[str, set[str]] = {}
    for name in names:
        players[name] = gen_player_achievements()
        print(f"Player {name}: {players[name]}")

    all_achievements = set[str]()
    for achs in players.values():
        all_achievements = all_achievements.union(achs)
    print(f"All distinct achievements: {all_achievements}")

    common = set(ALL_ACHIEVEMENTS)
    for achs in players.values():
        common = common.intersection(achs)
    print(f"Common achievements: {common}")

    for name in names:
        others: set[str] = set()
        for other_name in names:
            if other_name != name:
                others = others.union(players[other_name])
        unique = players[name].difference(others)
        print(f"Only {name} has: {unique}")

    full_set = set(ALL_ACHIEVEMENTS)
    for name in names:
        missing = full_set.difference(players[name])
        print(f"{name} is missing: {missing}")


if __name__ == "__main__":
    main()
