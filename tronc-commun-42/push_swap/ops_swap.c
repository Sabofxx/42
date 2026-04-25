/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ops_swap.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle             #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static void	swap_top(t_node **stack)
{
	t_node	*first;
	t_node	*second;

	if (!*stack || !(*stack)->next)
		return ;
	first = *stack;
	second = first->next;
	first->next = second->next;
	second->next = first;
	*stack = second;
}

void	op_sa(t_node **a, t_ctx *ctx)
{
	swap_top(a);
	log_op(ctx, OP_SA, "sa\n");
}

void	op_sb(t_node **b, t_ctx *ctx)
{
	swap_top(b);
	log_op(ctx, OP_SB, "sb\n");
}

void	op_ss(t_node **a, t_node **b, t_ctx *ctx)
{
	swap_top(a);
	swap_top(b);
	log_op(ctx, OP_SS, "ss\n");
}
