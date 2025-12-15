#include "BSQ.h"

static void	ft_free_int_matrix(int **map, int rows)
{
	int	idx;

	if (map == NULL)
		return ;
	idx = 0;
	while (idx < rows)
	{
		free(map[idx]);
		idx++;
	}
	free(map);
}

int	ft_min(int a, int b, int c)
{
	if (a <= b && a <= c)
		return (a);
	else if (b <= a && b <= c)
		return (b);
	else
		return (c);
}

int	**ft_generate_map(int l, int c)
{
	int	**map2;
	int	i;

	i = 0;
	if ((map2 = malloc(l * sizeof(int *))) == NULL)
		return (NULL);
	while (i < l)
	{
		if ((map2[i] = malloc(c * sizeof(int))) == NULL)
		{
			ft_free_int_matrix(map2, i);
			return (NULL);
		}
		i++;
	}
	return (map2);
}

int	ft_biggest_square(char **map, int c, int l, char o)
{
	int	i;
	int	j;
	int	**c_m;
	int	count_max;

	i = 0;
	count_max = 0;
	c_m = ft_generate_map(l, c);
	if (c_m == NULL)
		return (0);
	while (i < l)
	{
		j = 0;
		while (j < c - 1)
		{
			if (map[i][j] == o)
				c_m[i][j] = 0;
			else if (i == 0 || j == 0)
				c_m[i][j] = 1;
			else
				c_m[i][j] = ft_min(c_m[i - 1][j], c_m[i][j - 1], c_m[i - 1][j
						- 1]) + 1;
			if (c_m[i][j] > count_max)
				count_max = c_m[i][j];
			j++;
		}
		i++;
	}
	ft_free_int_matrix(c_m, l);
	return (count_max);
}

int	ft_find_position_square(char **map, int c, int l, char o)
{
	int	i;
	int	j;
	int	**c_m;
	int	count_max;
	int	p;

	i = 0;
	p = 0;
	count_max = ft_biggest_square(map, c, l, o);
	c_m = ft_generate_map(l, c);
	if (c_m == NULL)
		return (0);
	while (i < l)
	{
		j = 0;
		while (j < c - 1)
		{
			if (map[i][j] == o)
				c_m[i][j] = 0;
			else if (i == 0 || j == 0)
				c_m[i][j] = 1;
			else
				c_m[i][j] = ft_min(c_m[i - 1][j], c_m[i][j - 1], c_m[i - 1][j
						- 1]) + 1;
			if (c_m[i][j] == count_max)
			{
				p = i * (c - 1) + j;
				ft_free_int_matrix(c_m, l);
				return (p);
			}
			j++;
		}
		i++;
	}
	ft_free_int_matrix(c_m, l);
	return (p);
}
