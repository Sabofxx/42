

#include <unistd.h>

int main(int ac, char **av)
{
	int i;
	i = 0;

	char mirror;
	
	if(ac == 2)
	{
		while(av[1][i])
		{
			if(av[1][i] >= 'a' && av[1][i] <= 'z')
			{
				mirror = 'z' - (av[1][i] - 'a');
				write(1, &mirror, 1);
			}
			else if(av[1][i] >= 'A' && av[1][i] <= 'Z')
			{
				mirror = 'Z' - (av[1][i] - 'A');
				write(1, &mirror, 1);
			}
			else
				write(1, &av[1][i], 1);
		i++;
		}
	}
	write(1, "\n", 1);
}
