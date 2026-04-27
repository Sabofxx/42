#!/usr/bin/env python3

def whisper_lipher(text: str, shift: int) -> str:
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shifted = (ord(char) - base + shift) % 26 + base
            result += chr(shifted)
        else:
            result += char
    return result


def main() -> None:
    print(whisper_lipher("hello", 3))         # "khoor"
    print(whisper_lipher("Hello World!", 1))  # "Ifmmp Xpsme!"
    print(whisper_lipher("xyz", 3))           # "abc"
    print(whisper_lipher("ABC123def", 5))     # "FGH123ijk"
    print(whisper_lipher("", 10))             # ""


if __name__ == "__main__":
    main()
