


#include <unistd.h>


void ft_putchar(char c, int i)
{
	while (i > 0)
	{
		write(1, &c, 1);
		i--;
	}
}


int main(int ac, char **av)
{
	int i;
	i = 0;
	if(ac == 2)
	{
		while(av[1][i])
		{
			if(av[1][i] >= 'a' && av[1][i] <= 'z')
			{
				ft_putchar(av[1][i], av[1][i] - 'a' + 1);
			}
			else if(av[1][i] >= 'A' && av[1][i] <= 'Z')
			{
				ft_putchar(av[1][i], av[1][i] - 'A' + 1);
			}
			else
				write(1, &av[1][i], 1);
		i++;
		}
	}
	write(1, "\n", 1);
}
