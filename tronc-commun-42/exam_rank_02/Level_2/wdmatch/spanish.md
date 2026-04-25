## Subject

```C
Nombre de la asignación: wdmatch
Archivos esperados: wdmatch.c
Funciones permitidas: write
--------------------------------------------------------------------------------

Escribe un programa que tome dos cadenas y compruebe si es posible
escribir la primera cadena con caracteres de la segunda cadena, respetando
el orden en que estos caracteres aparecen en la segunda cadena.

Si es posible, el programa muestra la cadena, seguida de un \n, de lo contrario
simplemente muestra un \n.

Si el número de argumentos no es 2, el programa muestra un \n.

Ejemplos:

$>./wdmatch "faya" "fgvvfdxcacpolhyghbreda" | cat -e
faya$
$>./wdmatch "faya" "fgvvfdxcacpolhyghbred" | cat -e
$
$>./wdmatch "quarante deux" "qfqfsudf arzgsayns tsregfdgs sjytdekuoixq " | cat -e
quarante deux$
$>./wdmatch "error" rrerrrfiiljdfxjyuifrrvcoojh | cat -e
$
$>./wdmatch | cat -e
$

```