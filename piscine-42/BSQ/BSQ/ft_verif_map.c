#include "BSQ.h"

int	ft_verif_map(char *argv)
{
	if (ft_get_number_columns(argv) < 1 || ft_get_number_lines(argv) < 1)
	{
		ft_putstr("map error\n");
		return (1);
	}
	if (ft_verif_chars(argv) == 1 || ft_verif_returns(argv) == 1)
	{
		ft_putstr("map error\n");
		return (1);
	}
	if (ft_verif_columns(argv) == 1)
	{
		ft_putstr("map error\n");
		return (1);
	}
	return (0);
}
