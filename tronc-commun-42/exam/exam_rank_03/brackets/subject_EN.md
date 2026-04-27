# Brackets
---

Write a function:
```
def brackets(s: str) -> bool:
```
that takes a string s and returns True if all brackets in the string are correctly matched, properly nested, and closed, and False otherwise.

```
brackets("()")               → True
brackets("([{}])")           → True
brackets("(]")               → False
brackets("([)")              → False
brackets("a(b[c]d)")         → True
brackets("[{adaudna}]")      → True
brackets("[{adaudna}])")     → False
brackets("abc{[123(xyz)]}")  → True
```