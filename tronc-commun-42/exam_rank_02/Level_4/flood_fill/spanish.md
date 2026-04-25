## Subject

```C
Nombre de la tarea: flood_fill
Archivos esperados: *.c, *.h
Funciones permitidas: -
--------------------------------------------------------------------------------

Escribe una función que tome un char ** como un array bidimensional de char, un
t_point como las dimensiones de este array y un t_point como el punto de inicio.

Comenzando desde el 'begin' t_point dado, esta función llena una zona completa
reemplazando los caracteres adentro con el carácter 'F'. Una zona es un grupo de
caracteres iguales delimitados horizontal y verticalmente por otros caracteres
o los límites del array.

La función flood_fill no llenará en diagonal.

La función flood_fill tendrá un prototipo como este:
  void  flood_fill(char **tab, t_point size, t_point begin);

La estructura t_point se define así:

  typedef struct  s_point
  {
    int           x;
    int           y;
  }               t_point;

Ejemplo:

$> cat test.c
#include <stdlib.h>
#include <stdio.h>
#include "flood_fill.h"

char** make_area(char** zone, t_point size)
{
	char** new;

	new = malloc(sizeof(char*) * size.y);
	for (int i = 0; i < size.y; ++i)
	{
		new[i] = malloc(size.x + 1);
		for (int j = 0; j < size.x; ++j)
			new[i][j] = zone[i][j];
		new[i][size.x] = '\0';
	}

	return new;
}

int main(void)
{
	t_point size = {8, 5};
	char *zone[] = {
		"11111111",
		"10001001",
		"10010001",
		"10110001",
		"11100001",
	};

	char**  area = make_area(zone, size);
	for (int i = 0; i < size.y; ++i)
		printf("%s\n", area[i]);
	printf("\n");

	t_point begin = {7, 4};
	flood_fill(area, size, begin);
	for (int i = 0; i < size.y; ++i)
		printf("%s\n", area[i]);
	return (0);
}

$> gcc flood_fill.c test.c -o test; ./test
11111111
10001001
10010001
10110001
11100001

FFFFFFFF
F000F00F
F00F000F
F0FF000F
FFF0000F
$>
```