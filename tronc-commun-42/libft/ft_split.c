/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_split.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/15 15:24:34 by omischle           #+#    #+#             */
/*   Updated: 2026/01/15 15:40:03 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static size_t	ft_count_words(char const *s, char c)
{
	size_t	i;
	size_t	words;

	i = 0;
	words = 0;
	while (s[i])
	{
		while (s[i] && s[i] == c)
			i++;
		if (s[i] && s[i] != c)
		{
			words++;
			while (s[i] && s[i] != c)
				i++;
		}
	}
	return (words);
}

static void	ft_free_split(char **tab, size_t filled)
{
	size_t	i;

	i = 0;
	while (i < filled)
	{
		free(tab[i]);
		i++;
	}
	free(tab);
}

static int	ft_fill_split(char **tab, char const *s, char c, size_t words)
{
	size_t	i;
	size_t	k;
	size_t	start;

	i = 0;
	k = 0;
	while (k < words)
	{
		while (s[i] && s[i] == c)
			i++;
		start = i;
		while (s[i] && s[i] != c)
			i++;
		tab[k] = ft_substr(s, (unsigned int)start, i - start);
		if (!tab[k])
		{
			ft_free_split(tab, k);
			return (0);
		}
		k++;
	}
	tab[k] = NULL;
	return (1);
}

char	**ft_split(char const *s, char c)
{
	size_t	words;
	char	**tab;

	if (!s)
		return (NULL);
	words = ft_count_words(s, c);
	tab = (char **)malloc(sizeof(char *) * (words + 1));
	if (!tab)
		return (NULL);
	if (!ft_fill_split(tab, s, c, words))
		return (NULL);
	return (tab);
}
// #include <stdio.h>
// int	main(void)
// {
// 	char **t;
// 	int i;
// 	t = ft_split("  driss  wsh  42  ", ' ');
// 	i = 0;
// 	while (t && t[i])
// 	{
// 		printf("%s\n", t[i]);
// 		free(t[i]);
// 		i++;
// 	}
// 	free(t);
// 	return (0);
// }
