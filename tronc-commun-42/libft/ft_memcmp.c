/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memcmp.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 11:47:47 by omischle           #+#    #+#             */
/*   Updated: 2026/01/13 16:26:40 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

int	ft_memcmp(const void *s1, const void *s2, size_t n)
{
	size_t				i;
	const unsigned char	*p1;
	const unsigned char	*p2;

	p1 = (const unsigned char *)s1;
	p2 = (const unsigned char *)s2;
	i = 0;
	while (i < n)
	{
		if (p1[i] != p2[i])
			return (p1[i] - p2[i]);
		i++;
	}
	return (0);
}
// #include <stdio.h>
// #include <string.h>
// #include "libft.h"
// int	main(void)
// {
// 	char	a[] = {1, 2, 3, 4};
// 	char	b[] = {1, 2, 5, 4};
// 	printf("ft_memcmp: %d\n", ft_memcmp(a, b, 4));
// 	printf("   memcmp: %d\n", memcmp(a, b, 4));
// 	printf("ft_memcmp (equal): %d\n", ft_memcmp(a, a, 4));
// 	printf("   memcmp (equal): %d\n", memcmp(a, a, 4));
// 	return (0);
// }
