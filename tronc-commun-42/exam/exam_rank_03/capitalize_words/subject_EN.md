# capitalize_words
---
Write a function:
```
def capitalize_words(s: str) -> str:
```
that takes a string s and returns a new string where the first letter of each word is converted to uppercase and the rest remain lowercase.

#### Rules
Words are sequences of characters separated by spaces.
Preserve multiple spaces or punctuation exactly as in the original string.
Only alphabetic characters are affected; numbers and symbols remain unchanged.

#### Examples
```
capitalize_words("hello world")       → "Hello World"
capitalize_words("42 madrid exam")   → "42 Madrid Exam"
capitalize_words("  multiple   spaces ") → "  Multiple   Spaces "
capitalize_words("mixed CASE letters") → "Mixed Case Letters
```