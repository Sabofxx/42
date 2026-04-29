/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strtrim.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/14 19:48:05 by omischle          #+#    #+#             */
/*   Updated: 2026/01/15 15:24:09 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static int	ft_in_set(char c, char const *set)
{
	size_t	i;

	i = 0;
	while (set[i])
	{
		if (set[i] == c)
			return (1);
		i++;
	}
	return (0);
}

char	*ft_strtrim(char const *s1, char const *set)
{
	size_t	start;
	size_t	end;

	if (!s1 || !set)
		return (NULL);
	start = 0;
	while (s1[start] && ft_in_set(s1[start], set))
		start++;
	end = ft_strlen(s1);
	while (end > start && ft_in_set(s1[end - 1], set))
		end--;
	return (ft_substr(s1, (unsigned int)start, end - start));
}
// #include <stdio.h>
// int	main(void)
// {
// 	char *s = "  \t\ndrissssss  \n";
// 	char *set = " \n\t";
// 	char *r;
// 	r = ft_strtrim(s, set);
// 	printf("%s\n", r);
// 	free(r);
// 	r = ft_strtrim("xxxx42xxxxxxxxxxxxxxxxxxxxxx", "x");
// 	printf("%s\n", r);
// 	free(r);
// 	return (0);
// }