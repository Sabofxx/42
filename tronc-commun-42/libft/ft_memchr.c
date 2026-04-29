/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memchr.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 11:47:41 by omischle          #+#    #+#             */
/*   Updated: 2026/01/13 16:26:46 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	*ft_memchr(const void *s, int c, size_t n)
{
	size_t			i;
	unsigned char	*ptr;
	unsigned char	ch;

	ptr = (unsigned char *)s;
	ch = (unsigned char)c;
	i = 0;
	while (i < n)
	{
		if (ptr[i] == ch)
			return ((void *)(ptr + i));
		i++;
	}
	return (NULL);
}
// #include <stdio.h>
// #include <string.h>
// int	main(void)
// {
// 	char	data[] = "hello\0world";
// 	printf("ft_memchr: %p\n", ft_memchr(data, 'o', 11));
// 	printf("   memchr: %p\n", memchr(data, 'o', 11));
// 	printf("ft_memchr (not found): %p\n", ft_memchr(data, 'z', 11));
// 	printf("   memchr (not found): %p\n", memchr(data, 'z', 11));
// 	return (0);
// }
