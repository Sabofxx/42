#!/usr/bin/env python3

def brackets(string: str) -> bool:
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}

    for char in string:
        if char in '([{':
            stack.append(char)
        elif char in ')]}':
            if not stack or pairs[char] != stack[-1]:
                return False
            stack.pop()
    return len(stack) == 0


def main() -> None:
    print(brackets("()"))
    print(brackets("([{}])"))
    print(brackets("(]"))


if __name__ == "__main__":
    main()
