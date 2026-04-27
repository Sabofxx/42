def py_echo_validator(text: str) -> bool:
    filtered = [c.lower() for c in text if c.isalpha()]
    if not filtered:
        return False
    return filtered == filtered[::-1]
