/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle             #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static void	init_ctx(t_ctx *ctx)
{
	int	i;

	ctx->forced = STRAT_ADAPTIVE;
	ctx->used = STRAT_ADAPTIVE;
	ctx->bench = 0;
	ctx->disorder = 0.0;
	ctx->total = 0;
	i = 0;
	while (i < 11)
		ctx->ops[i++] = 0;
}

int	main(int argc, char **argv)
{
	t_node	*a;
	t_node	*b;
	t_ctx	ctx;
	int		parse;

	a = NULL;
	b = NULL;
	init_ctx(&ctx);
	if (argc < 2)
		return (0);
	parse = parse_input(argc, argv, &a, &ctx);
	if (parse == 2)
		return (0);
	if (!parse)
		error_exit(&a, &b, NULL);
	assign_indexes(a);
	run_strategy(&a, &b, &ctx);
	if (ctx.bench)
		print_bench(&ctx);
	free_stack(&a);
	return (0);
}
