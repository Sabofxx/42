def atoi(s: str) -> int:
    s = s.strip()
    sign = 1
    i = 0
    result = 0

    if i < len(s) and s[i] in '-+':
        sign = -1 if s[i] == '-' else 1
        i += 1

    while i < len(s) and s[i].isdigit()
        result = result * 10 + int(s[i])
        i += 1

    return result * sign 