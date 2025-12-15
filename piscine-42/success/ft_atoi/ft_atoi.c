

#include <stdio.h>

int	ft_atoi(const char *str)
{
	int i;
	int sign;
	int r;

	i = 0;
	sign = 1;
	r = 0;

	while((str[i] >= 9 && str[i] <= 13) || (str[i] == ' '))
		i++;
	if (str[i] == '-' )
	{
			sign *= -1;
			i++;
	}
	if (str[i] == '+')
		i++;
	while(str[i] >= '0' && str[i] <= '9')
	{
		r = (r * 10) + (str[i] - '0');
		i++;
	}
	return (r * sign);
}


/*int main()
{
	char str[] = "       1234";

	printf("%d", ft_atoi(str));
}*/
