## Subject

```C
Nombre de la tarea: ft_list_remove_if
Archivos esperados: ft_list_remove_if.c
Funciones permitidas: free
--------------------------------------------------------------------------------

Escribe una función llamada ft_list_remove_if que elimine de la lista
pasada cualquier elemento cuyos datos sean "iguales" a los datos de referencia.

Se declarará de la siguiente manera:

void ft_list_remove_if(t_list **begin_list, void *data_ref, int (*cmp)());

cmp toma dos void* y devuelve 0 cuando ambos parámetros son iguales.

Debes usar el archivo ft_list.h, que contendrá:

$>cat ft_list.h
typedef struct      s_list
{
    struct s_list   *next;
    void            *data;
}                   t_list;
$>

```