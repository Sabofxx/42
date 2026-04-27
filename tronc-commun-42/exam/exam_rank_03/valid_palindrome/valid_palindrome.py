#!/usr/bin/env python3

def valid_palindrome(s: str) -> bool:
    filtered = "".join(c.lower() for c in s if c.isalnum())
    return filtered == filtered[::-1]


def main() -> None:
    print(valid_palindrome("Was it a car or a cat I saw?"))    # True
    print(valid_palindrome("tab a cat"))                       # False
    print(valid_palindrome("A man, a plan, a canal: Panama"))  # True
    print(valid_palindrome("No lemon, no melon"))              # True
    print(valid_palindrome(""))                                # True


if __name__ == "__main__":
    main()
