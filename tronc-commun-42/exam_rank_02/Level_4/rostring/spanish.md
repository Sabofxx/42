## Subject

```C
Nombre de la tarea: rostring
Archivos esperados: rostring.c
Funciones permitidas: write, malloc, free
--------------------------------------------------------------------------------

Escribe un programa que tome una cadena y muestre esta cadena después de rotarla
una palabra hacia la izquierda.

Así, la primera palabra se convierte en la última, y las demás se mantienen en el mismo orden.

Una "palabra" se define como una parte de una cadena delimitada por espacios/tabulaciones, o
por el inicio/fin de la cadena.

Las palabras estarán separadas por solo un espacio en la salida.

Si hay menos de un argumento, el programa muestra \n.

Ejemplo:

$>./rostring "abc   " | cat -e
abc$
$>
$>./rostring "Que la      lumiere soit et la lumiere fut"
la lumiere soit et la lumiere fut Que
$>
$>./rostring "     AkjhZ zLKIJz , 23y"
zLKIJz , 23y AkjhZ
$>
$>./rostring "first" "2" "11000000"
first
$>
$>./rostring | cat -e
$
$>

```