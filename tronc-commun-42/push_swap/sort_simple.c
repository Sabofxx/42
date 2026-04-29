/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sort_simple.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static void	push_min_from_a(t_node **a, t_node **b, t_ctx *ctx)
{
	int	pos;
	int	size;

	pos = find_min_pos(*a);
	size = stack_size(*a);
	if (pos <= size / 2)
	{
		while (pos-- > 0)
			op_ra(a, ctx);
	}
	else
	{
		while (pos++ < size)
			op_rra(a, ctx);
	}
	op_pb(a, b, ctx);
}

void	simple_sort(t_node **a, t_node **b, t_ctx *ctx)
{
	int	size;

	size = stack_size(*a);
	if (size <= 1)
		return ;
	if (size <= 5)
		return (sort_small_to_five(a, b, ctx));
	while (stack_size(*a) > 3)
		push_min_from_a(a, b, ctx);
	sort_three(a, ctx);
	while (*b)
		op_pa(a, b, ctx);
}
