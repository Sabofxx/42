def capitalize_words(s: str) -> str:
    words = s.split(" ")
    capitalized = [w.capitalize() for w in words]
    return " ".join(capitalized)
