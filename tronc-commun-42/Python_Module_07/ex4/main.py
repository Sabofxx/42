from ex4.TournamentCard import TournamentCard
from ex4.TournamentPlatform import TournamentPlatform


def main() -> None:
    print("=== DataDeck Tournament Platform ===")
    print()

    platform = TournamentPlatform()

    print("Registering Tournament Cards...")
    dragon = TournamentCard(
        "Fire Dragon", 5, "Legendary", 7, 5
    )
    wizard = TournamentCard(
        "Ice Wizard", 4, "Epic", 4, 6, 1150
    )

    d_id = platform.register_card(dragon)
    w_id = platform.register_card(wizard)

    print(f"Fire Dragon (ID: {d_id}):")
    print(
        "- Interfaces:"
        " [Card, Combatable, Rankable]"
    )
    info = dragon.get_rank_info()
    print(f"- Rating: {info['rating']}")
    print(f"- Record: {info['record']}")

    print(f"Ice Wizard (ID: {w_id}):")
    print(
        "- Interfaces:"
        " [Card, Combatable, Rankable]"
    )
    info = wizard.get_rank_info()
    print(f"- Rating: {info['rating']}")
    print(f"- Record: {info['record']}")

    print()
    print("Creating tournament match...")
    result = platform.create_match(d_id, w_id)
    print(f"Match result: {result}")

    print()
    print("Tournament Leaderboard:")
    for entry in platform.get_leaderboard():
        print(
            f"{entry['rank']}. {entry['name']}"
            f" - Rating: {entry['rating']}"
            f" ({entry['record']})"
        )

    print()
    print("Platform Report:")
    print(platform.generate_tournament_report())

    print()
    print(
        "=== Tournament Platform"
        " Successfully Deployed! ==="
    )
    print(
        "All abstract patterns working"
        " together harmoniously!"
    )


if __name__ == "__main__":
    main()
