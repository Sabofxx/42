/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parse.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle             #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	parse_tokens(char **tokens, int count, t_node **a);
int	split_count(char **tokens);
int	fill_tokens_from_argv(int argc, char **argv, char **tokens);

static int	startswith_dashdash(const char *s)
{
	return (s[0] == '-' && s[1] == '-');
}

static int	read_flag(char *arg, t_ctx *ctx)
{
	if (ft_strcmp(arg, "--bench") == 0)
		ctx->bench = 1;
	else if (ft_strcmp(arg, "--simple") == 0)
		ctx->forced = STRAT_SIMPLE;
	else if (ft_strcmp(arg, "--medium") == 0)
		ctx->forced = STRAT_MEDIUM;
	else if (ft_strcmp(arg, "--complex") == 0)
		ctx->forced = STRAT_COMPLEX;
	else if (ft_strcmp(arg, "--adaptive") == 0)
		ctx->forced = STRAT_ADAPTIVE;
	else
		return (0);
	return (1);
}

static int	count_total_numbers(int argc, char **argv, t_ctx *ctx)
{
	char	**split;
	int		i;
	int		total;

	i = 1;
	total = 0;
	while (i < argc)
	{
		if (startswith_dashdash(argv[i]))
		{
			if (!read_flag(argv[i], ctx))
				return (-1);
		}
		else
		{
			split = ft_split_spaces(argv[i]);
			if (!split || split_count(split) == 0)
				return (free_split(split), -1);
			total += split_count(split);
			free_split(split);
		}
		i++;
	}
	return (total);
}

int	parse_input(int argc, char **argv, t_node **a, t_ctx *ctx)
{
	char	**tokens;
	int		total;
	int		ok;

	total = count_total_numbers(argc, argv, ctx);
	if (total < 0)
		return (0);
	if (total == 0)
		return (2);
	tokens = (char **)malloc(sizeof(char *) * (total + 1));
	if (!tokens)
		return (0);
	ok = fill_tokens_from_argv(argc, argv, tokens);
	if (ok)
		ok = parse_tokens(tokens, total, a);
	free_split(tokens);
	return (ok);
}
