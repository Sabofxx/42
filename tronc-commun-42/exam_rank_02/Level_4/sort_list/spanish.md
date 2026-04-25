## Subject

```C
Nombre de la tarea: sort_list
Archivos esperados: sort_list.c
Funciones permitidas:
--------------------------------------------------------------------------------

Escribe las siguientes funciones:

t_list	*sort_list(t_list* lst, int (*cmp)(int, int));

Esta función debe ordenar la lista dada como parámetro, usando el puntero a función cmp para seleccionar el orden a aplicar, y devuelve un puntero al primer elemento de la lista ordenada.

Las duplicaciones deben permanecer.

Las entradas siempre serán consistentes.

Debes usar el tipo t_list descrito en el archivo list.h
que se te proporciona. Debes incluir ese archivo
(#include "list.h"), pero no debes entregarlo. Usaremos el nuestro
para compilar tu tarea.

Las funciones pasadas como cmp siempre devolverán un valor diferente de
0 si a y b están en el orden correcto, 0 en caso contrario.

Por ejemplo, la siguiente función utilizada como cmp ordenará la lista
en orden ascendente:

int ascending(int a, int b)
{
	return (a <= b);
}

```