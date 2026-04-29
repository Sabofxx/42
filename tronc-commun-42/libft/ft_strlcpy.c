/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strlcpy.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/14 16:10:27 by omischle          #+#    #+#             */
/*   Updated: 2026/01/14 18:40:51 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

size_t	ft_strlcpy(char *dst, const char *src, size_t dstsize)
{
	size_t	i;
	size_t	slen;

	slen = 0;
	while (src[slen])
		slen++;
	if (dstsize == 0)
		return (slen);
	i = 0;
	while (src[i] && i + 1 < dstsize)
	{
		dst[i] = src[i];
		i++;
	}
	dst[i] = '\0';
	return (slen);
}
// #include <stdio.h>
// #include <string.h>
// int	main(void)
// {
// 	char a[10];
// 	char b[10];
// 	printf("%zu | %s\n", ft_strlcpy(a, "driss", 10), a);
// 	printf("%zu | %s\n", strlcpy(b, "driss", 10), b);
// 	return (0);
// }