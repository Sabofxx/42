def whisper_lipher(text: str, shift: int) -> str:
    shift = shift % 26

    lower = "abcdefghijklmnopqrstuvwxyz"
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    shifted_lower = lower[shift:] + lower[:shift]
    shifted_upper = upper[shift:] + upper[:shift]

    translation_table = str.maketrans(
        lower + upper, shifted_lower + shifted_upper)

    return text.translate(translation_table)
