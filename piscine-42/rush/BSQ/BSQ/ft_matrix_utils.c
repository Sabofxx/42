/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_matrix_utils.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/15 13:03:30 by omischle          #+#    #+#             */
/*   Updated: 2025/12/15 13:03:33 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "BSQ.h"

int	ft_min(int a, int b, int c)
{
	if (a <= b && a <= c)
		return (a);
	if (b <= a && b <= c)
		return (b);
	return (c);
}

void	ft_free_int_matrix(int **map, int rows)
{
	int	index;

	if (map == NULL)
		return ;
	index = 0;
	while (index < rows)
	{
		free(map[index]);
		index++;
	}
	free(map);
}

int	**ft_generate_map(int lines, int columns)
{
	int	**matrix;
	int	row;

	matrix = malloc(lines * sizeof(int *));
	if (matrix == NULL)
		return (NULL);
	row = 0;
	while (row < lines)
	{
		matrix[row] = malloc(columns * sizeof(int));
		if (matrix[row] == NULL)
		{
			ft_free_int_matrix(matrix, row);
			return (NULL);
		}
		row++;
	}
	return (matrix);
}
