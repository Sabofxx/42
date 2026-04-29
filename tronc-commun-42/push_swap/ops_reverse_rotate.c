/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ops_reverse_rotate.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static void	reverse_rotate(t_node **stack)
{
	t_node	*prev;
	t_node	*last;

	if (!*stack || !(*stack)->next)
		return ;
	prev = NULL;
	last = *stack;
	while (last->next)
	{
		prev = last;
		last = last->next;
	}
	prev->next = NULL;
	last->next = *stack;
	*stack = last;
}

void	op_rra(t_node **a, t_ctx *ctx)
{
	reverse_rotate(a);
	log_op(ctx, OP_RRA, "rra\n");
}

void	op_rrb(t_node **b, t_ctx *ctx)
{
	reverse_rotate(b);
	log_op(ctx, OP_RRB, "rrb\n");
}

void	op_rrr(t_node **a, t_node **b, t_ctx *ctx)
{
	reverse_rotate(a);
	reverse_rotate(b);
	log_op(ctx, OP_RRR, "rrr\n");
}
