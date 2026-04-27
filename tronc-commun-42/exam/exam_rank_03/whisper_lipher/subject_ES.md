# py_whisper_lipher

Escribe una función 
```
def whisper_lipher(text: str, shift: int) -> str:
```

* Aplique un cifrado César al texto recibido, desplazando cada letra shift posiciones en el alfabeto.
* Respete mayúsculas y minúsculas (una letra mayúscula sigue siendo mayúscula).
* Los caracteres que no sean letras (espacios, puntuación, números) se dejan sin cambiar.
* El desplazamiento debe ser circular (después de 'z' vuelve a 'a').

### Ejemplo
```
whisper_lipher("Hello, World!", 3)  →  "Khoor, Zruog!"
whisper_lipher("abc", 1)            →  "bcd"
whisper_lipher("xyz", 2)            →  "zab"
```