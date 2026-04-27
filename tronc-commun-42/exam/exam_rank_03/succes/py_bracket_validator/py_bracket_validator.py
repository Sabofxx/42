def py_bracket_validator(s: str) -> bool:
    pairs = {')': '(', ']': '[', '}': '{'}
    openers = set('([{')
    stack: list[str] = []
    for c in s:
        if c in openers:
            stack.append(c)
        elif c in pairs:
            if not stack or stack[-1] != pairs[c]:
                return False
            stack.pop()
    return len(stack) == 0
