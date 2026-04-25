## Subject

```c
Nombre de la tarea: expand_str
Archivos esperados: expand_str.c
Funciones permitidas: write
--------------------------------------------------------------------------------

Escribe un programa que tome una cadena y la muestre con exactamente tres espacios
entre cada palabra, sin espacios ni tabulaciones ni al principio ni al final,
seguido de un salto de línea.

Una palabra es una sección de cadena delimitada ya sea por espacios/tabulaciones, o por
el principio/fin de la cadena.

Si el número de parámetros no es 1, o si no hay palabras, simplemente muestra
un salto de línea.

Ejemplos:

$> ./expand_str "See? It's easy to print the same thing" | cat -e
See?   It's   easy   to   print   the   same   thing$
$> ./expand_str " this        time it      will     be    more complex  " | cat -e
this   time   it   will   be   more   complex$
$> ./expand_str "No S*** Sherlock..." "nAw S*** ShErLaWQ..." | cat -e
$
$> ./expand_str "" | cat -e
$
$>

```
