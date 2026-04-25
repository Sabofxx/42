## Subject

```C
Nombre de la tarea: repeat_alpha
Archivos esperados: repeat_alpha.c
Funciones permitidas: write
--------------------------------------------------------------------------------

Escribe un programa llamado repeat_alpha que tome una cadena y la muestre
repitiendo cada carácter alfabético tantas veces como su índice alfabético,
seguido de un salto de línea.

'a' se convierte en 'a', 'b' se convierte en 'bb', 'e' se convierte en 'eeeee', etc...

El caso permanece sin cambios.

Si el número de argumentos no es 1, solo muestra un salto de línea.

Ejemplos:

$>./repeat_alpha "abc"
abbccc
$>./repeat_alpha "Alex." | cat -e
Alllllllllllleeeeexxxxxxxxxxxxxxxxxxxxxxxx.$
$>./repeat_alpha 'abacadaba 42!' | cat -e
abbacccaddddabba 42!$
$>./repeat_alpha | cat -e
$
$>
$>./repeat_alpha "" | cat -e
$
$>

```