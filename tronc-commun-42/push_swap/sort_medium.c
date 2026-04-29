/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sort_medium.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	int_sqrt(int n)
{
	int	i;

	i = 1;
	while (i * i <= n)
		i++;
	return (i - 1);
}

static void	push_chunks(t_node **a, t_node **b, t_ctx *ctx, int chunk)
{
	int	pushed;
	int	limit;

	pushed = 0;
	limit = chunk;
	while (*a)
	{
		if ((*a)->index <= pushed)
		{
			op_pb(a, b, ctx);
			op_rb(b, ctx);
			pushed++;
		}
		else if ((*a)->index <= limit)
		{
			op_pb(a, b, ctx);
			pushed++;
		}
		else
			op_ra(a, ctx);
		if (pushed >= limit)
			limit += chunk;
	}
}

void	medium_sort(t_node **a, t_node **b, t_ctx *ctx)
{
	int	chunk;
	int	pos;

	chunk = int_sqrt(stack_size(*a)) + 1;
	push_chunks(a, b, ctx, chunk);
	while (*b)
	{
		pos = find_max_pos(*b);
		if (pos <= stack_size(*b) / 2)
			while (pos-- > 0)
				op_rb(b, ctx);
		else
			while (pos++ < stack_size(*b))
				op_rrb(b, ctx);
		op_pa(a, b, ctx);
	}
}
