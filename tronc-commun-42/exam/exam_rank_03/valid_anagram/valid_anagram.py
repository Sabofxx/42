#!/usr/bin/env python3

def valid_anagram(s: str, t: str) -> bool:
    return sorted(s) == sorted(t)


def main() -> None:
    print(valid_anagram("racecar", "carrace"))  # True
    print(valid_anagram("jar", "jam"))          # False
    print(valid_anagram("listen", "silent"))    # True
    print(valid_anagram("aabbcc", "abcabc"))    # True
    print(valid_anagram("abc", "ab"))           # False


if __name__ == "__main__":
    main()
