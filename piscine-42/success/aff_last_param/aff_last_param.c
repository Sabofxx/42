
#include <unistd.h>

int main(int ac,char **av)
{
	int a;
	int i;
	
	a = ac - 1;
	i = 0;

	if (ac > 1)
	{
		while(av[a][i])
		{
			write(1, &av[a][i], 1);
			i++;
		}
	}
	write(1, "\n", 1);
}
