def whisper_lipher(text: str, shift: int) -> str:
    shift %= 26

    def shift_char(c):
        if 'a' <= c <= 'z':
            return chr((ord(c) - ord('a') + shift) % 26 + ord('a'))
        if 'A' <= c <= 'Z':
            return chr((ord(c) - ord('A') + shift) % 26 + ord('A'))
        return c

    return ''.join(map(shift_char, text))
