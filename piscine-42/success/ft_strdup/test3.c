



#include <stdlib.h>
#include <stdio.h>

char    *ft_strdup(char *src)
{
	char *i;
	int length;

	length = 0;

	while(src[length])
		length++;
	i = malloc(sizeof(char) * (length - 1));
	length = 0;
	while(src[length])
	{
	*i = src[length];
		length++;
	}
	return(src);
}

int main()
{
	char src[] = "jesaisas";

	printf("%s\n", ft_strdup(src));
}
