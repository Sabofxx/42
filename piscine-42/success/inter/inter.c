

#include <unistd.h>

int iter(char *str, char c, int len)
{
	int i;
	i = 0;
	while(str[i] && (len == -1 || len > i))
	{
		if(str[i] == c)
			return (1);
		i++;
	}
	return (0);
}

int main(int ac, char **av)
{
	int i;
	i = 0;

	if(ac == 3)
	{
		while(av[1][i])
		{
			if(!iter(av[1], av[1][i], i) && iter(av[2], av[1][i], -1))
			{
				write(1, &av[1][i], 1);
			}
		i++;
		}
	}
	write(1, "\n", 1);
	return (0);
}
