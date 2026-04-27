#!/usr/bin/env python3

VOWELS = set("aeiouAEIOU")


def vowel_count(s: str) -> int:
    return sum(1 for c in s if c in VOWELS)


def cryptic_sorter(strings: list[str]) -> list[str]:
    return sorted(strings, key=lambda s: (len(s), s.lower(), vowel_count(s), s))


def main() -> None:
    print(cryptic_sorter(["apple", "cat", "banana", "dog", "elephant"]))
    # ['cat', 'dog', 'apple', 'banana', 'elephant']
    print(cryptic_sorter(["aaa", "bbb", "AAA", "BBB"]))
    # ['AAA', 'aaa', 'BBB', 'bbb']
    print(cryptic_sorter(["hello", "world", "hi", "test"]))
    # ['hi', 'test', 'hello', 'world']
    print(cryptic_sorter([]))    # []
    print(cryptic_sorter([""]))  # ['']


if __name__ == "__main__":
    main()
