/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_find_solution.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/15 13:03:30 by omischle          #+#    #+#             */
/*   Updated: 2025/12/15 13:03:33 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "BSQ.h"

static int	ft_cell_value(t_dp_ctx *ctx, int row, int col)
{
	if (ctx->map[row][col] == ctx->info.obstacle)
		return (0);
	if (row == 0 || col == 0)
		return (1);
	return (ft_min(ctx->cache[row - 1][col], ctx->cache[row][col - 1],
			ctx->cache[row - 1][col - 1]) + 1);
}

static void	ft_update_row(t_dp_ctx *ctx, t_square *result, int row)
{
	int	col;
	int	position;

	col = 0;
	while (col < ctx->info.columns - 1)
	{
		ctx->cache[row][col] = ft_cell_value(ctx, row, col);
		if (ctx->cache[row][col] > result->size)
		{
			result->size = ctx->cache[row][col];
			position = row * (ctx->info.columns - 1) + col;
			result->position = position;
		}
		col++;
	}
}

t_square	ft_find_square(char **map, t_bsq_info info)
{
	t_square	result;
	t_dp_ctx	ctx;
	int			row;

	result.size = 0;
	result.position = 0;
	if (map == NULL || info.columns <= 0 || info.lines <= 0)
		return (result);
	ctx.map = map;
	ctx.info = info;
	ctx.cache = ft_generate_map(info.lines, info.columns);
	if (ctx.cache == NULL)
		return (result);
	row = 0;
	while (row < info.lines)
	{
		ft_update_row(&ctx, &result, row);
		row++;
	}
	ft_free_int_matrix(ctx.cache, info.lines);
	return (result);
}

int	ft_biggest_square(char **map, t_bsq_info info)
{
	t_square	result;

	result = ft_find_square(map, info);
	return (result.size);
}

int	ft_find_position_square(char **map, t_bsq_info info)
{
	t_square	result;

	result = ft_find_square(map, info);
	return (result.position);
}
