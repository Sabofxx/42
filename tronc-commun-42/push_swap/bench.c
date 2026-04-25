/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   bench.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle             #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static void	print_percent(double v)
{
	long	scaled;

	scaled = (long)(v * 10000.0 + 0.5);
	ft_putnbr_fd(scaled / 100, 2);
	write(2, ".", 1);
	if ((scaled % 100) < 10)
		write(2, "0", 1);
	ft_putnbr_fd(scaled % 100, 2);
}

static void	print_strategy(t_ctx *ctx)
{
	if (ctx->forced == STRAT_ADAPTIVE)
		ft_putstr_fd("adaptive -> ", 2);
	if (ctx->used == STRAT_SIMPLE)
		ft_putstr_fd("simple (O(n^2))", 2);
	else if (ctx->used == STRAT_MEDIUM)
		ft_putstr_fd("medium (O(n*sqrt(n)))", 2);
	else if (ctx->used == STRAT_COMPLEX)
		ft_putstr_fd("complex (O(n log n))", 2);
}

void	print_bench(t_ctx *ctx)
{
	static const char	*names[11] = {"sa", "sb", "ss", "pa", "pb", "ra",
		"rb", "rr", "rra", "rrb", "rrr"};
	int					i;

	ft_putstr_fd("[bench] disorder: ", 2);
	print_percent(ctx->disorder);
	ft_putstr_fd("%\n[bench] strategy: ", 2);
	print_strategy(ctx);
	ft_putstr_fd("\n[bench] total_ops: ", 2);
	ft_putnbr_fd(ctx->total, 2);
	i = 0;
	while (i < 11)
	{
		ft_putstr_fd("\n[bench] ", 2);
		ft_putstr_fd(names[i], 2);
		ft_putstr_fd(": ", 2);
		ft_putnbr_fd(ctx->ops[i], 2);
		i++;
	}
	write(2, "\n", 1);
}
