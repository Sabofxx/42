## Subject

```C
Nombre de la asignación: union
Archivos esperados: union.c
Funciones permitidas: write
--------------------------------------------------------------------------------

Escribe un programa que tome dos cadenas y muestre, sin duplicados, los
caracteres que aparecen en alguna de las dos cadenas.

La visualización será en el orden en que aparecen los caracteres en la línea de comandos y
será seguida de un \n.

Si el número de argumentos no es 2, el programa mostrará \n.

Ejemplo:

$>./union zpadinton "paqefwtdjetyiytjneytjoeyjnejeyj" | cat -e
zpadintoqefwjy$
$>./union ddf6vewg64f gtwthgdwthdwfteewhrtag6h4ffdhsd | cat -e
df6vewg4thras$
$>./union "rien" "cette phrase ne cache rien" | cat -e
rienct phas$
$>./union | cat -e
$
$>
$>./union "rien" | cat -e
$
$>

```