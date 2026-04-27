_VOWELS = set('aeiouAEIOU')


def _vowel_count(s: str) -> int:
    return sum(1 for c in s if c in _VOWELS)


def py_cryptic_sorter(strings: list[str]) -> list[str]:
    return sorted(strings, key=lambda s: (len(s), s.lower(), _vowel_count(s), s))
