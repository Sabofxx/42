/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parse_utils.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	has_duplicate(int *arr, int size, int val)
{
	int	i;

	i = 0;
	while (i < size)
	{
		if (arr[i] == val)
			return (1);
		i++;
	}
	return (0);
}

static int	convert_values(char **tokens, int count, int *values)
{
	int		i;
	int		ok;
	long	v;

	i = 0;
	while (i < count)
	{
		v = ft_atol(tokens[i], &ok);
		if (!ok || has_duplicate(values, i, (int)v))
			return (0);
		values[i] = (int)v;
		i++;
	}
	return (1);
}

int	build_stack_from_values(int *values, int count, t_node **a)
{
	int		i;
	t_node	*node;

	i = 0;
	while (i < count)
	{
		node = stack_new(values[i]);
		if (!node)
			return (0);
		stack_add_back(a, node);
		i++;
	}
	return (1);
}

int	parse_tokens(char **tokens, int count, t_node **a)
{
	int	*values;
	int	ok;

	values = (int *)malloc(sizeof(int) * count);
	if (!values)
		return (0);
	ok = convert_values(tokens, count, values);
	if (ok)
		ok = build_stack_from_values(values, count, a);
	free(values);
	return (ok);
}
