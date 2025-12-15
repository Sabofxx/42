

#include <unistd.h>


void	wdmatch(char *str1, char *str2)
{
	int		len;
	int		i;

	i = 0;
	len = 0;
	while (str1[len])
		len++;
	while (i < len && *str2)
	{
		if(str1[i] == *str2)
			i++;
	str2++;
	}
	if (i == len)
		write(1, str1, len);
}

int		main(int argc, char **argv)
{
	if (argc == 3)
		wdmatch(argv[1], argv[2]);
	write(1, "\n", 1);
	return (0);
}
