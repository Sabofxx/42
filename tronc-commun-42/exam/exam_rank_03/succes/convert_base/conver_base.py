#!/usr/bin/env python3

def convert_base(number: str, from_base: int, to_base: int) -> str:
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    try:
        if not (2 <= from_base <= 36 and 2 <= to_base <= 36):
            return "ERROR"
        decimal = int(number, from_base)
    except ValueError:
        return "ERROR"

    if decimal == 0:
        return "0"

    result = ""
    while decimal > 0:
        result = digits[decimal % to_base] + result
        decimal //= to_base
    return result


def main() -> None:
    print(convert_base("ff", 16, 2))   # "11111111"
    print(convert_base("10", 2, 10))   # "2"
    print(convert_base("1g", 16, 10))  # "ERROR"
    print(convert_base("Z", 36, 10))   # "35"
    print(convert_base("0", 10, 16))   # "0"


if __name__ == "__main__":
    main()
