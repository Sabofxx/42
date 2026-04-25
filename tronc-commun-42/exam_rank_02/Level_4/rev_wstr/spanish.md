## Subject

```C
Nombre de la tarea: rev_wstr
Archivos esperados: rev_wstr.c
Funciones permitidas: write, malloc, free
--------------------------------------------------------------------------------

Escribe un programa que tome una cadena como parámetro y imprima sus palabras en
orden inverso.

Una "palabra" es una parte de la cadena delimitada por espacios y/o tabulaciones, o el
inicio/fin de la cadena.

Si el número de parámetros es diferente de 1, el programa mostrará
'\n'.

En los parámetros que serán probados, no habrá "espacios adicionales" (lo que significa que no habrá espacios adicionales al principio o al final de la cadena, y las palabras siempre estarán separadas por exactamente un espacio).

Ejemplos:

$> ./rev_wstr "You hate people! But I love gatherings. Isn't it ironic?" | cat -e
ironic? it Isn't gatherings. love I But people! hate You$
$>./rev_wstr "abcdefghijklm"
abcdefghijklm
$> ./rev_wstr "Wingardium Leviosa" | cat -e
Leviosa Wingardium$
$> ./rev_wstr | cat -e
$
$>

```