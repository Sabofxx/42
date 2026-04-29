/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sort_small.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	sort_three(t_node **a, t_ctx *ctx)
{
	int	f;
	int	s;
	int	t;

	f = (*a)->index;
	s = (*a)->next->index;
	t = (*a)->next->next->index;
	if (f > s && s < t && f < t)
		op_sa(a, ctx);
	else if (f > s && s > t)
	{
		op_sa(a, ctx);
		op_rra(a, ctx);
	}
	else if (f > s && s < t && f > t)
		op_ra(a, ctx);
	else if (f < s && s > t && f < t)
	{
		op_sa(a, ctx);
		op_ra(a, ctx);
	}
	else if (f < s && s > t && f > t)
		op_rra(a, ctx);
}

static void	push_smallest_to_b(t_node **a, t_node **b, t_ctx *ctx)
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

void	sort_small_to_five(t_node **a, t_node **b, t_ctx *ctx)
{
	while (stack_size(*a) > 3)
		push_smallest_to_b(a, b, ctx);
	sort_three(a, ctx);
	while (*b)
		op_pa(a, b, ctx);
}
