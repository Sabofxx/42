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

t_square	ft_find_square(char **map, t_bsq_info info);

char	**ft_fill_map(char **map, t_bsq_info info)
{
	t_square	square;
	int			base_row;
	int			base_col;
	int			row;
	int			col;

	if (map == NULL || info.columns <= 1 || info.lines <= 0)
		return (map);
	square = ft_find_square(map, info);
	if (square.size <= 0)
		return (map);
	base_row = (square.position / (info.columns - 1)) - square.size + 1;
	base_col = (square.position % (info.columns - 1)) - square.size + 1;
	row = base_row;
	while (row < base_row + square.size)
	{
		col = base_col;
		while (col < base_col + square.size)
		{
			map[row][col] = info.full;
			col++;
		}
		row++;
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

void	ft_print_solution(int index, char **argv)
{
	t_bsq_info	info;
	char		**map;
	int			row;

	info.obstacle = ft_get_char_obst(argv[index]);
	info.full = ft_get_char_full(argv[index]);
	info.columns = ft_get_number_columns(argv[index]);
	info.lines = ft_get_number_lines(argv[index]);
	if (info.columns <= 0 || info.lines <= 0)
		return ;
	map = ft_read_file(argv[index]);
	if (map == NULL)
		return ;
	ft_fill_map(map, info);
	row = 0;
	while (row < info.lines)
	{
		ft_putstr(map[row]);
		ft_putchar('\n');
		row++;
	}
	ft_free_char_map(map, info.lines);
}

int	main(int argc, char **argv)
{
	int	index;

	if (argc < 2)
		return (0);
	index = 1;
	while (index < argc)
	{
		if (ft_verif_map(argv[index]) == 0)
			ft_print_solution(index, argv);
		index++;
	}
	return (0);
}
