#!/usr/bin/env python3

def atoi(s: str) -> int:
    s = s.strip()
    sign = 1
    i = 0
    result = 0

    if i < len(s) and s[i] in "+-":
        sign = -1 if s[i] == "-" else 1
        i += 1

    while i < len(s) and s[i].isdigit():
        result = result * 10 + int(s[i])
        i += 1
    return sign * result


def main() -> None:
    print(atoi("42"))        # 42
    print(atoi("  -42ab"))   # -42
    print(atoi("+123"))      # 123
    print(atoi("abc"))       # 0
    print(atoi("   007"))    # 7


if __name__ == "__main__":
    main()
