#!/usr/bin/env python3


def py_string_sculptor(text: str) -> str:
    result = ""
<<<<<<< Updated upstream
    lower = True

    for c in text:
        if c.isspace():
            lower = True
            result += c
        elif c.isalpha():
            if lower:
                result += c.lower()
            else:
                result += c.upper()
            lower = not lower
=======
    lower_next = True
    for c in text:
        if c.isspace():
            lower_next = True
            result += c
        elif c.isalpha():
            if lower_next:
                result += c.lower()
            else:
                result += c.upper()
            lower_next = not lower_next
>>>>>>> Stashed changes
        else:
            result += c
    return result

def main() -> None:
    print(py_string_sculptor("hello"))  # "hElLo"
    print(py_string_sculptor("Hello World"))  # "hElLo wOrLd"
    print(py_string_sculptor("aBc123def"))  # "aBc123DeF"
    print(py_string_sculptor("Python3.9!"))  # "pYtHoN3.9!"
    print(py_string_sculptor(""))  # ""


if __name__ == "__main__":
    main()
