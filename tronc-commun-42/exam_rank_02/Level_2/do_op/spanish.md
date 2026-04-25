## Subject

```C
Nombre de la asignación: do_op
Archivos esperados: *.c, *.h
Funciones permitidas: atoi, printf, write
--------------------------------------------------------------------------------

Escribe un programa que tome tres cadenas:
- La primera y la tercera son representaciones de enteros con signo en base 10
  que caben en un int.
- La segunda es un operador aritmético elegido de: + - * / %

El programa debe mostrar el resultado de la operación aritmética solicitada,
seguido de una nueva línea. Si el número de parámetros no es 3, el programa
simplemente muestra una nueva línea.

Puedes asumir que las cadenas no tienen errores ni caracteres extraños. Los números negativos,
en la entrada o en la salida, tendrán un y solo un '-' inicial. El
resultado de la operación cabe en un int.

Ejemplos:

$> ./do_op "123" "*" 456 | cat -e
56088$
$> ./do_op "9828" "/" 234 | cat -e
42$
$> ./do_op "1" "+" "-43" | cat -e
-42$
$> ./do_op | cat -e
$

```