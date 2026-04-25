## Subject

```C
Nombre de la tarea: rot_13
Archivos esperados: rot_13.c
Funciones permitidas: write
--------------------------------------------------------------------------------

Escribe un programa que tome una cadena y la muestre, reemplazando cada una de sus
letras por la letra 13 espacios adelante en orden alfabético.

'z' se convierte en 'm' y 'Z' se convierte en 'M'. El caso permanece sin cambios.

La salida estará seguida de un salto de línea.

Si el número de argumentos no es 1, el programa muestra un salto de línea.

Ejemplo:

$>./rot_13 "abc"
nop
$>./rot_13 "My horse is Amazing." | cat -e
Zl ubefr vf Nznmvat.$
$>./rot_13 "AkjhZ zLKIJz , 23y " | cat -e
NxwuM mYXVWm , 23l $
$>./rot_13 | cat -e
$
$>
$>./rot_13 "" | cat -e
$
$>

```