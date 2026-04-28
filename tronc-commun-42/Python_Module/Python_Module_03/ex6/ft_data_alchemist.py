import random


def main() -> None:
    print("=== Game Data Alchemist ===")
    players = [
        "Alice", "bob", "Charlie", "dylan",
        "Emma", "Gregory", "john", "kevin", "Liam",
    ]
    print(f"Initial list of players: {players}")

    all_caps = [n.capitalize() for n in players]
    print(
        "New list with all names"
        f" capitalized: {all_caps}"
    )

    only_caps = [n for n in players if n[0].isupper()]
    print(
        "New list of capitalized names"
        f" only: {only_caps}"
    )

    scores = {
        n: random.randint(0, 1000) for n in all_caps
    }
    print(f"Score dict: {scores}")

    avg = round(sum(scores.values()) / len(scores), 2)
    print(f"Score average is {avg}")

    high = {
        k: v for k, v in scores.items() if v > avg
    }
    print(f"High scores: {high}")


if __name__ == "__main__":
    main()
