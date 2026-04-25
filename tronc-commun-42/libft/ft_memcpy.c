/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memcpy.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 11:47:50 by omischle           #+#    #+#             */
/*   Updated: 2026/01/14 18:42:54 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	*ft_memcpy(void *dst, const void *src, size_t n)
{
	size_t				i;
	unsigned char		*d;
	const unsigned char	*s;

	if (!dst && !src)
		return (NULL);
	d = (unsigned char *)dst;
	s = (const unsigned char *)src;
	i = 0;
	while (i < n)
	{
		d[i] = s[i];
		i++;
	}
	return (dst);
}
// #include <stdio.h>
// #include <string.h>
// #include "libft.h"

// int	main(void)
// {
// 	char	src[] = "driss";
// 	char	dst1[10];
// 	char	dst2[10];

// 	ft_memcpy(dst1, src, 6);
// 	memcpy(dst2, src, 6);

// 	printf("ft_memcpy: %s\n", dst1);
// 	printf("   memcpy: %s\n", dst2);

// 	return (0);
// }
