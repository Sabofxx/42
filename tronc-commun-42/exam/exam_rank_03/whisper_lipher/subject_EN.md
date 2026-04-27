# py_whisper_lipher

Write a function
```
def whisper_lipher(text: str, shift: int) -> str:
```

* Apply a Caesar cipher to the given text, shifting each letter by shift positions in the alphabet.
* Preserve uppercase and lowercase (an uppercase letter remains uppercase).
* Non-letter characters (spaces, punctuation, numbers) should remain unchanged.
* The shift must be circular (after 'z' it wraps around to 'a').

### Examples
```
whisper_lipher("Hello, World!", 3)  →  "Khoor, Zruog!"
whisper_lipher("abc", 1)            →  "bcd"
whisper_lipher("xyz", 2)            →  "zab"
```