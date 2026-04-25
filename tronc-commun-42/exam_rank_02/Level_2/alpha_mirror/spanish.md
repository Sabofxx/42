## Subject

```C
Nombre de la asignación: alpha_mirror
Archivos esperados: alpha_mirror.c
Funciones permitidas: write
--------------------------------------------------------------------------------

Escribe un programa llamado alpha_mirror que tome una cadena y muestre esta cadena
después de reemplazar cada carácter alfabético por el carácter alfabético opuesto,
seguido de una nueva línea.

'a' se convierte en 'z', 'Z' se convierte en 'A'
'd' se convierte en 'w', 'M' se convierte en 'N'

y así sucesivamente.

No se cambia el caso de las letras.

Si el número de argumentos no es 1, muestra solo una nueva línea.

Ejemplos:

$>./alpha_mirror "abc"
zyx
$>./alpha_mirror "My horse is Amazing." | cat -e
Nb slihv rh Znzarmt.$
$>./alpha_mirror | cat -e
$
$>
````