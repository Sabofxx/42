# capitalize_words
---
Escribe una función:
```
def capitalize_words(s: str) -> str:
```
que recibe una cadena s y devuelve una nueva cadena donde la primera letra de cada palabra se convierte en mayúscula y el resto permanece en minúscula.

#### Reglas
Las palabras son secuencias de caracteres separadas por espacios.  
Se deben preservar los espacios múltiples y la puntuación exactamente como en la cadena original.  
Solo se modifican los caracteres alfabéticos; los números y símbolos permanecen sin cambios.

#### Ejemplos
```
capitalize_words("hello world")       → "Hello World"
capitalize_words("42 madrid exam")   → "42 Madrid Exam"
capitalize_words("  multiple   spaces ") → "  Multiple   Spaces "
capitalize_words("mixed CASE letters") → "Mixed Case Letters
```