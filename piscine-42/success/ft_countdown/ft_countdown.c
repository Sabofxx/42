
#include <unistd.h>

void	ft_countdown()
{
	char c;
	c = '9';

	while(c >= '0')
	{
		write(1, &c, 1);
		c--;
	}
	write(1, "\n", 1);
}

int main()
{
	ft_countdown();
}
