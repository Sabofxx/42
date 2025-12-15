/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_print_solution.c                                :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/15 13:04:04 by omischle          #+#    #+#             */
/*   Updated: 2025/12/15 13:04:05 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "BSQ.h"

char	**ft_fill_map(char **map, int c, int l, char o, char p)
{
	int	i;
	int	j;
	int	length;
	int	pos;

	if (map == NULL || c <= 1 || l <= 0)
		return (map);
	length = ft_biggest_square(map, c, l, o);
	pos = ft_find_position_square(map, c, l, o);
	i = (pos / (c - 1)) - length + 1;
	while (i < (pos / (c - 1)) + 1)
	{
		j = (pos % (c - 1)) - length + 1;
		while (j < (pos % (c - 1)) + 1)
		{
			map[i][j] = p;
			j++;
		}
		i++;
	}
	return (map);
}

static void	ft_free_char_map(char **map, int l)
{
	int	idx;

	if (map == NULL)
		return ;
	idx = 0;
	while (idx < l)
	{
		free(map[idx]);
		idx++;
	}
	free(map);
}

void	ft_print_solution(int i, char **argv)
{
	char	**map;
	int		j;
	int		c;
	int		l;
	char	o;
	char	p;

	map = NULL;
	j = 0;
	o = ft_get_char_obst(argv[i]);
	p = ft_get_char_full(argv[i]);
	c = ft_get_number_columns(argv[i]);
	l = ft_get_number_lines(argv[i]);
	if (c <= 0 || l <= 0)
		return ;
	map = ft_read_file(argv[i]);
	if (map == NULL)
		return ;
	ft_fill_map(map, c, l, o, p);
	while (j < l)
	{
		ft_putstr(map[j]);
		ft_putchar('\n');
		j++;
	}
	ft_free_char_map(map, l);
}

int	main(int argc, char **argv)
{
	int	i;

	i = 1;
	if (argc > 1)
	{
		while (i < argc)
		{
			if ((ft_verif_map(argv[i])) == 1)
				;
			else
			{
				ft_print_solution(i, argv);
			}
			i++;
		}
	}
	else
		return (0);
}
