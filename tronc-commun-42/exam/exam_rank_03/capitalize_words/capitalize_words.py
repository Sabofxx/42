#!/usr/bin/env python3

def capitalize_words(s: str) -> str:
    words = s.split(" ")
    capitalized = [w.capitalize() for w in words]
    return " ".join(capitalized)


def main() -> None:
    print(capitalize_words("hello world"))           # "Hello World"
    print(capitalize_words("42 madrid exam"))        # "42 Madrid Exam"
    print(capitalize_words("  multiple   spaces "))  # "  Multiple   Spaces "
    print(capitalize_words("mixed CASE letters"))    # "Mixed Case Letters"


if __name__ == "__main__":
    main()
