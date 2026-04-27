#!/usr/bin/env python3


def capitalize_words(s: str) -> str:
    words = s.split(" ")
    capitalized_words = [word.capitalize() for word in words]
    return " ".join(capitalized_words)


def capitalize_words_manual(s: str) -> str:
    result = ""
    new_word = True

    for char in s:
        if char.isalpha():
            if new_word:
                result += char.upper()
                new_word = False
            else:
                result += char.lower()
        else:
            result += char
            if char == " ":
                new_word = True

    return result


def main() -> None:
    print(capitalize_words("hello world"))  # "Hello World"
    print(capitalize_words("42 madrid exam"))  # "42 Madrid Exam"
    print(capitalize_words("  multiple   spaces "))  # "  Multiple   Spaces "
    print(capitalize_words("mixed CASE letters"))  # "Mixed Case Letters"


if __name__ == "__main__":
    main()
