/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strlcat.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/14 16:10:31 by omischle           #+#    #+#             */
/*   Updated: 2026/01/14 18:43:19 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

size_t	ft_strlcat(char *dst, const char *src, size_t dstsize)
{
	size_t	dlen;
	size_t	slen;
	size_t	i;

	dlen = 0;
	while (dlen < dstsize && dst[dlen])
		dlen++;
	slen = 0;
	while (src[slen])
		slen++;
	if (dlen == dstsize)
		return (dstsize + slen);
	i = 0;
	while (src[i] && dlen + i + 1 < dstsize)
	{
		dst[dlen + i] = src[i];
		i++;
	}
	dst[dlen + i] = '\0';
	return (dlen + slen);
}
// #include <stdio.h>
// #include <string.h>
// int	main(void)
// {
// 	char a[20] = "Driss";
// 	char b[20] = "Driss";
// 	printf("%zu | %s\n", ft_strlcat(a, " Ssird", 20), a);
// 	printf("%zu | %s\n", strlcat(b, " Ssird", 20), b);
// 	return (0);
// }
