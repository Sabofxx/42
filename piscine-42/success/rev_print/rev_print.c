
#include <unistd.h>

void	ft_putchar(char c)
{
	write(1, &c, 1);
}

int main(int ac, char **av)
{
	int i;
	i = 0;
	
	if (ac == 2)
	{
		while(av[1][i])	
			i++;
		i--;
		while(i >= 0)
		{
			write(1, &av[1][i], 1);
			i--;
		}
	}
	write(1, "\n", 1);
}
