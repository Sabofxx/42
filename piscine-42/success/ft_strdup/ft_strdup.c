
#include <stdlib.h>
#include <stdio.h>

char	*ft_strdup(char *src)
{
	int		length;
	char	*result;

	length = 0;
	while (src[length])
		length++;
	result = malloc(sizeof(char) * length + 1);
	length = 0;
	while (src[length])
	{
		result[length] = src[length];
		length++;
	}
	return (result);
}

int		main(void)
{
	char	*result;

	result = ft_strdup("Hello!");
	printf("%s\n", result);
	return (0);
}
