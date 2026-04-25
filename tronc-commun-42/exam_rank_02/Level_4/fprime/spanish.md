## Subject

```C
Nombre de la tarea: fprime
Archivos esperados: fprime.c
Funciones permitidas: printf, atoi
--------------------------------------------------------------------------------

Escribe un programa que tome un entero positivo y muestre sus factores primos en la
salida estándar, seguido de una nueva línea.

Los factores deben mostrarse en orden ascendente y separados por '*', de modo que
la expresión en la salida dé el resultado correcto.

Si el número de parámetros no es 1, simplemente muestra una nueva línea.

La entrada, cuando la hay, será válida.

Ejemplos:

$> ./fprime 225225 | cat -e
3*3*5*5*7*11*13$
$> ./fprime 8333325 | cat -e
3*3*5*5*7*11*13*37$
$> ./fprime 9539 | cat -e
9539$
$> ./fprime 804577 | cat -e
804577$
$> ./fprime 42 | cat -e
2*3*7$
$> ./fprime 1 | cat -e
1$
$> ./fprime | cat -e
$
$> ./fprime 42 21 | cat -e
$
```