import random
from typing import Generator


PLAYERS = ["alice", "bob", "charlie", "dylan"]
ACTIONS = [
    "run", "eat", "sleep", "grab", "move",
    "climb", "swim", "release", "use",
]


def gen_event() -> Generator[
    tuple[str, str], None, None
]:
    """Endless generator yielding random events."""
    while True:
        name = random.choice(PLAYERS)
        action = random.choice(ACTIONS)
        yield (name, action)


def consume_event(
    events: list[tuple[str, str]]
) -> Generator[tuple[str, str], None, None]:
    """Yield random events from list, removing each."""
    while len(events) > 0:
        idx = random.randint(0, len(events) - 1)
        event = events[idx]
        events.pop(idx)
        yield event


def main() -> None:
    print("=== Game Data Stream Processor ===")
    gen = gen_event()
    for i in range(1000):
        name, action = next(gen)
        print(
            f"Event {i}: Player {name}"
            f" did action {action}"
        )

    event_list = [next(gen) for _ in range(10)]
    print(f"Built list of 10 events: {event_list}")

    for event in consume_event(event_list):
        print(f"Got event from list: {event}")
        print(f"Remains in list: {event_list}")


if __name__ == "__main__":
    main()
