def valid_anagram(s: str, t: str) -> bool:
    return sorted(s) == sorted(t)