/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   strategy.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle             #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static t_strategy	pick_adaptive(double disorder)
{
	if (disorder < 0.2)
		return (STRAT_SIMPLE);
	if (disorder < 0.5)
		return (STRAT_MEDIUM);
	return (STRAT_COMPLEX);
}

static void	run_selected(t_node **a, t_node **b, t_ctx *ctx)
{
	if (ctx->used == STRAT_SIMPLE)
		simple_sort(a, b, ctx);
	else if (ctx->used == STRAT_MEDIUM)
		medium_sort(a, b, ctx);
	else if (ctx->used == STRAT_COMPLEX)
		complex_sort(a, b, ctx);
}

void	run_strategy(t_node **a, t_node **b, t_ctx *ctx)
{
	if (!*a || is_sorted(*a))
		return ;
	ctx->disorder = compute_disorder(*a);
	ctx->used = ctx->forced;
	if (ctx->forced == STRAT_ADAPTIVE)
		ctx->used = pick_adaptive(ctx->disorder);
	run_selected(a, b, ctx);
}
