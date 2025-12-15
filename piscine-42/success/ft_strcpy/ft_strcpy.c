
#include <stdio.h>

char    *ft_strcpy(char *s1, char *s2)
{
	int i;
	i = 0;

	while(s2[i])
	{
		s1[i] = s2[i];
		i++;
	}
	return (s1);
}

/*
int main()
{
	char str1[] = "jesios";
	char str2[] = "jspppp";

	printf("%s\n",ft_strcpy(str1,str2));
}
*/
