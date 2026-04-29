/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_substr.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/14 17:38:53 by omischle          #+#    #+#             */
/*   Updated: 2026/01/14 18:38:47 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_substr(char const *s, unsigned int start, size_t len)
{
	size_t	i;
	size_t	slen;
	char	*sub;

	if (!s)
		return (NULL);
	slen = 0;
	while (s[slen])
		slen++;
	if (start >= slen)
		return (ft_strdup(""));
	if (len > slen - start)
		len = slen - start;
	sub = (char *)malloc(len + 1);
	if (!sub)
		return (NULL);
	i = 0;
	while (i < len)
	{
		sub[i] = s[start + i];
		i++;
	}
	sub[i] = '\0';
	return (sub);
}
// #include <stdio.h>
// int	main(void)
// {
// 	char *s = "driss";
// 	char *sub;
// 	sub = ft_substr(s, 1, 3);
// 	printf("%s\n", sub);
// 	free(sub);
// 	sub = ft_substr(s, 0, 5);
// 	printf("%s\n", sub);
// 	free(sub);
// 	return (0);
// }