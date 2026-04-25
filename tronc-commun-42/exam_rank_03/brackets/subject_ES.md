# Brackets
---

Escribe una función:
```
def brackets(s: str) -> bool:
```
que recibe una cadena s y devuelve True si todos los paréntesis en la cadena están correctamente emparejados, bien anidados y cerrados, y False en caso contrario.

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