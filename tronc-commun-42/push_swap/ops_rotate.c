/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ops_rotate.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle             #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static void	rotate(t_node **stack)
{
	t_node	*first;
	t_node	*last;

	if (!*stack || !(*stack)->next)
		return ;
	first = *stack;
	*stack = first->next;
	first->next = NULL;
	last = *stack;
	while (last->next)
		last = last->next;
	last->next = first;
}

void	op_ra(t_node **a, t_ctx *ctx)
{
	rotate(a);
	log_op(ctx, OP_RA, "ra\n");
}

void	op_rb(t_node **b, t_ctx *ctx)
{
	rotate(b);
	log_op(ctx, OP_RB, "rb\n");
}

void	op_rr(t_node **a, t_node **b, t_ctx *ctx)
{
	rotate(a);
	rotate(b);
	log_op(ctx, OP_RR, "rr\n");
}
