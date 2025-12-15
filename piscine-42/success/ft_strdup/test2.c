
#include <stdio.h>
#include <stdlib.h>

char *ft_strdup(const char *src)
{
	char *result;
	int length;

	length = 0;

	while(src[length])
		length++;
	result = malloc(sizeof(char) * (length + 1));
	length = 0;
	while(src[length])
	{
		result[length] = src[length];
		length++;
	}
	return (result);
}

int main()
{
	char *str = ft_strdup("drissjspfrr");
	printf("%s\n", str);
}
