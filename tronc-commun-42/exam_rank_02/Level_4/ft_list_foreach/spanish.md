## Subject

```C
Nombre de la tarea: ft_list_foreach
Archivos esperados: ft_list_foreach.c, ft_list.h
Funciones permitidas:
--------------------------------------------------------------------------------

Escribe una función que tome una lista y un puntero a función, y aplique esta
función a cada elemento de la lista.

Debe ser declarada de la siguiente manera:

void    ft_list_foreach(t_list *begin_list, void (*f)(void *));

La función apuntada por f se usará de la siguiente manera:

(*f)(list_ptr->data);

Debes usar la siguiente estructura y entregarla en un archivo llamado
ft_list.h:

typedef struct    s_list
{
    struct s_list *next;
    void          *data;
}                 t_list;

````