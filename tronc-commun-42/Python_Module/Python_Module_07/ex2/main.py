from ex2.EliteCard import EliteCard


def main() -> None:
    print("=== DataDeck Ability System ===")
    print()

    print("EliteCard capabilities:")
    print(
        "- Card: ['play', 'get_card_info',"
        " 'is_playable']"
    )
    print(
        "- Combatable: ['attack', 'defend',"
        " 'get_combat_stats']"
    )
    print(
        "- Magical: ['cast_spell',"
        " 'channel_mana', 'get_magic_stats']"
    )

    print()
    warrior = EliteCard(
        "Arcane Warrior", 6, "Legendary",
        5, 8, 4
    )

    print("Playing Arcane Warrior (Elite Card):")
    print("Combat phase:")
    atk = warrior.attack("Enemy")
    print(f"Attack result: {atk}")
    dfn = warrior.defend(5)
    print(f"Defense result: {dfn}")

    print()
    print("Magic phase:")
    spell = warrior.cast_spell(
        "Fireball", ["Enemy1", "Enemy2"]
    )
    print(f"Spell cast: {spell}")
    mana = warrior.channel_mana(3)
    print(f"Mana channel: {mana}")

    print()
    print(
        "Multiple interface"
        " implementation successful!"
    )


if __name__ == "__main__":
    main()
