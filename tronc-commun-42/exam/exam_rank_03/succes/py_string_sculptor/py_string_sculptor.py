def py_string_sculptor(text: str) -> str:
    result = []
    alpha_index = 0
    for c in text:
        if c.isspace():
            alpha_index = 0
            result.append(c)
        elif c.isalpha():
            if alpha_index % 2 == 0:
                result.append(c.lower())
            else:
                result.append(c.upper())
            alpha_index += 1
        else:
            result.append(c)
    return ''.join(result)
