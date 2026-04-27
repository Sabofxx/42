#!/usr/bin/env python3

def pattern_tracker(text: str) -> int:
    count = 0
    for i in range(len(text) - 1):
        a, b = text[i], text[i + 1]
        if a.isdigit() and b.isdigit() and int(b) - int(a) == 1:
            count += 1
    return count


def main() -> None:
    print(pattern_tracker("123"))         # 2
    print(pattern_tracker("12a34"))       # 2
    print(pattern_tracker("987654321"))   # 0
    print(pattern_tracker("01234567"))    # 7
    print(pattern_tracker("abc"))         # 0
    print(pattern_tracker("1a2b3c4"))     # 0
    print(pattern_tracker("112233"))      # 2


if __name__ == "__main__":
    main()
