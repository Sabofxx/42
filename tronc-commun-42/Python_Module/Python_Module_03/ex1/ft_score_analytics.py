import sys


def main() -> None:
    print("=== Player Score Analytics ===")
    usage = ("No scores provided. Usage: "
             "python3 ft_score_analytics.py <score1> <score2> ...")
    if len(sys.argv) == 1:
        print(usage)
        return
    scores: list[int] = []
    for arg in sys.argv[1:]:
        try:
            scores.append(int(arg))
        except ValueError:
            print(f"Invalid parameter: '{arg}'")
    if len(scores) == 0:
        print(usage)
        return
    print(f"Scores processed: {scores}")
    print(f"Total players: {len(scores)}")
    print(f"Total score: {sum(scores)}")
    print(f"Average score: {sum(scores) / len(scores)}")
    print(f"High score: {max(scores)}")
    print(f"Low score: {min(scores)}")
    print(f"Score range: {max(scores) - min(scores)}")


if __name__ == "__main__":
    main()
