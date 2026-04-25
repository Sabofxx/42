from ex3.FantasyCardFactory import FantasyCardFactory
from ex3.AggressiveStrategy import AggressiveStrategy
from ex3.GameEngine import GameEngine


def main() -> None:
    print("=== DataDeck Game Engine ===")
    print()

    factory = FantasyCardFactory()
    strategy = AggressiveStrategy()
    engine = GameEngine()

    print("Configuring Fantasy Card Game...")
    engine.configure_engine(factory, strategy)
    print("Factory: FantasyCardFactory")
    print("Strategy: AggressiveStrategy")
    types = factory.get_supported_types()
    print(f"Available types: {types}")

    print()
    print("Simulating aggressive turn...")

    hand = [
        factory.create_creature(),
        factory.create_creature("goblin"),
        factory.create_spell(),
    ]
    hand_str = ", ".join(
        f"{c.name} ({c.cost})" for c in hand
    )
    print(f"Hand: [{hand_str}]")

    engine.hand = hand
    result = engine.simulate_turn()
    print("Turn execution:")
    print(f"Strategy: {result['strategy']}")
    print(f"Actions: {result['actions']}")

    print()
    print("Game Report:")
    print(engine.get_engine_status())

    print()
    print(
        "Abstract Factory + Strategy Pattern:"
        " Maximum flexibility achieved!"
    )


if __name__ == "__main__":
    main()
