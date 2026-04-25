#!/usr/bin/env python3


def convert_base(number: str, from_base: int, to_base: int) -> str:
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    try:
        if not (2 <= from_base <= 36 and 2 <= to_base <= 36):
            print("ERROR")
            return

        decimal = int(number, from_base)
    except ValueError:
        print("ERROR")
        return

    if decimal == 0:
        print("0")
        return

    result = ""
    while decimal > 0:
        result = digits[decimal % to_base] + result
        decimal //= to_base
    print(result)


def main() -> None:
    convert_base("ff", 16, 2)
    convert_base("10", 2, 10)
    convert_base("1g", 16, 10)


if __name__ == "__main__":
    main()
