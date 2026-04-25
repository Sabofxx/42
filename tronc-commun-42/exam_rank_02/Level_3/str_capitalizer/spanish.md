## Subject

```c
Nombre de la tarea: str_capitalizer
Archivos esperados: str_capitalizer.c
Funciones permitidas: write
--------------------------------------------------------------------------------

Escribe un programa que tome una o varias cadenas y, para cada argumento,
capitalice el primer carácter de cada palabra (Si es una letra, obviamente),
ponga el resto en minúsculas, y muestre el resultado en la salida estándar,
seguido de un \n.

Una "palabra" se define como una parte de una cadena delimitada por espacios/tabulaciones o
por el inicio/fin de la cadena. Si una palabra tiene solo una letra, debe ser
capitalizada.

Si no hay argumentos, el programa debe mostrar \n.

Ejemplo:

$> ./str_capitalizer | cat -e
$
$> ./str_capitalizer "a FiRSt LiTTlE TESt" | cat -e
A First Little Test$
$> ./str_capitalizer "__SecONd teST A LITtle BiT   Moar comPLEX" "   But... This iS not THAT COMPLEX" "     Okay, this is the last 1239809147801 but not    the least    t" | cat -e
__second Test A Little Bit   Moar Complex$
   But... This Is Not That Complex$
     Okay, This Is The Last 1239809147801 But Not    The Least    T$
$>

```
