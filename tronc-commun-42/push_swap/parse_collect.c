/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parse_collect.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	split_count(char **tokens)
{
	int	count;

	count = 0;
	while (tokens[count])
		count++;
	return (count);
}

static int	startswith_dashdash(const char *s)
{
	return (s[0] == '-' && s[1] == '-');
}

int	fill_tokens_from_argv(int argc, char **argv, char **tokens)
{
	char	**split;
	int		i;
	int		j;
	int		k;

	i = 1;
	k = 0;
	while (i < argc)
	{
		if (!startswith_dashdash(argv[i]))
		{
			split = ft_split_spaces(argv[i]);
			if (!split)
				return (0);
			j = -1;
			while (split[++j])
				tokens[k++] = ft_strdup(split[j]);
			free_split(split);
		}
		i++;
	}
	tokens[k] = NULL;
	return (1);
}
