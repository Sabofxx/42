#!/usr/bin/env python3

def py_string_sculptor(text: str) -> str:
    result = ""
    alpha_index = 0
    for c in text:
        if c.isspace():
            alpha_index = 0
            result += c
        elif c.isalpha():
            if alpha_index % 2 == 0:
                result += c.lower()
            else:
                result += c.upper()
            alpha_index += 1
        else:
            result += c
    return result


def main() -> None:
    print(py_string_sculptor("hello"))         # "hElLo"
    print(py_string_sculptor("Hello World"))   # "hElLo wOrLd"
    print(py_string_sculptor("aBc123def"))     # "aBc123DeF"
    print(py_string_sculptor("Python3.9!"))    # "pYtHoN3.9!"
    print(py_string_sculptor(""))              # ""


if __name__ == "__main__":
    main()
