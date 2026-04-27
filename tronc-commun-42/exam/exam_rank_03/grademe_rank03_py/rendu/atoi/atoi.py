def atoi(s: str) -> int:
    result = 0
    sign = 1 
    i = 0

    s = s.strip()

    if i < len(s) and s[i] in '+-':
        sign = -1 if s[i] == '-' else 1
        i += 1

    while i < len(s) and s[i].isdigit():
        result = result * 10 + int(s[i])
        i += 1

    return result * sign


print(atoi("42"))
print(atoi("  -42abc")) 
print(atoi("+123"))
print(atoi("abc"))
