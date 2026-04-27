#!/usr/bin/env python3


def atoi(string: str) -> int:
    string = string.strip()
    sign = 1
    i = 0
    result = 0

    if i < len(string) and string[i] in "+-":
        sign = -1 if string[i] == "-" else 1
        i += 1

    while i < len(string) and string[i].isdigit():
        result = result * 10 + int(string[i])
        i += 1
    return sign * result


def main() -> None:
    print(atoi("42"))
    print(atoi("  -42ab"))
    print(atoi("+123"))
    print(atoi("abc"))


if __name__ == "__main__":
    main()
