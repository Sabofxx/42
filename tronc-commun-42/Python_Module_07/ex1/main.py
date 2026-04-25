from ex0.CreatureCard import CreatureCard
from ex1.SpellCard import SpellCard
from ex1.ArtifactCard import ArtifactCard
from ex1.Deck import Deck


def main() -> None:
    print("=== DataDeck Deck Builder ===")
    print()
    print("Building deck with different card types...")

    deck = Deck()
    dragon = CreatureCard(
        "Fire Dragon", 5, "Legendary", 7, 5
    )
    bolt = SpellCard(
        "Lightning Bolt", 3, "Common", "damage"
    )
    crystal = ArtifactCard(
        "Mana Crystal", 2, "Rare", 5,
        "+1 mana per turn"
    )

    deck.add_card(bolt)
    deck.add_card(crystal)
    deck.add_card(dragon)

    print(f"Deck stats: {deck.get_deck_stats()}")

    print()
    print("Drawing and playing cards:")
    game = {"mana": 10}

    for _ in range(3):
        card = deck.draw_card()
        info = card.get_card_info()
        ctype = info.get("type", "Unknown")
        print(f"Drew: {card.name} ({ctype})")
        result = card.play(game)
        print(f"Play result: {result}")
        print()

    print(
        "Polymorphism in action:"
        " Same interface, different card behaviors!"
    )


if __name__ == "__main__":
    main()
