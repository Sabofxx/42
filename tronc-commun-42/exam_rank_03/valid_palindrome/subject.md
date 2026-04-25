# Valid Palindrome
---
Write a function:
```
def valid_palindrome(s: str) -> bool:
```
Returns True if s is a palindrome, ignoring:
    * Case (uppercase/lowercase)
    * Non-alphanumeric characters
Returns False otherwise.

#### Examples
```
valid_palindrome("Was it a car or a cat I saw?") → True
valid_palindrome("tab a cat")                     → False
valid_palindrome("A man, a plan, a canal: Panama") → True
valid_palindrome("No lemon, no melon")           → True
```