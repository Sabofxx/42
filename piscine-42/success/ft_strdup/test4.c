

#include <stdlib.h>
#include <stdio.h>

char    *ft_strdup(char *src)
{
	char *caca;
	int length;

	length = 0;

	while(src[length])
		length++;
	caca = malloc(sizeof(char) * (length - 1));
	length = 0;
	while(src[length])
	{
		*caca = src[length];
		length++;
	}
	return (caca);
}

int main()
{
	char src[] = "drissestgay";

	printf("%s\n", src);
}
