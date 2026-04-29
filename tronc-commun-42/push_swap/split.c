/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   split.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	is_space(char c)
{
	return (c == ' ' || c == '\t' || c == '\n' || c == '\v'
		|| c == '\f' || c == '\r');
}

static int	word_count(const char *s)
{
	int	count;

	count = 0;
	while (*s)
	{
		while (*s && is_space(*s))
			s++;
		if (*s)
			count++;
		while (*s && !is_space(*s))
			s++;
	}
	return (count);
}

static char	*dup_word(const char *start, int len)
{
	char	*word;
	int		i;

	word = (char *)malloc(len + 1);
	if (!word)
		return (NULL);
	i = 0;
	while (i < len)
	{
		word[i] = start[i];
		i++;
	}
	word[len] = '\0';
	return (word);
}

static int	fill_words(char **out, const char *s)
{
	int		idx;
	int		len;
	char	*start;

	idx = 0;
	while (*s)
	{
		while (*s && is_space(*s))
			s++;
		if (!*s)
			break ;
		start = (char *)s;
		len = 0;
		while (*s && !is_space(*s))
		{
			len++;
			s++;
		}
		out[idx] = dup_word(start, len);
		if (!out[idx++])
			return (0);
	}
	out[idx] = NULL;
	return (1);
}

char	**ft_split_spaces(const char *s)
{
	char	**out;
	int		count;

	count = word_count(s);
	out = (char **)malloc(sizeof(char *) * (count + 1));
	if (!out)
		return (NULL);
	if (!fill_words(out, s))
	{
		free_split(out);
		return (NULL);
	}
	return (out);
}
