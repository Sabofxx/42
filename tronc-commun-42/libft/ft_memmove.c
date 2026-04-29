/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memmove.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 11:47:53 by omischle          #+#    #+#             */
/*   Updated: 2026/01/13 16:28:50 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	*ft_memmove(void *dst, const void *src, size_t len)
{
	long	i;

	if (dst < src)
	{
		i = 0;
		while ((size_t)i < len)
		{
			*(unsigned char *)(dst + i) = *(unsigned char *)(src + i);
			i++;
		}
		return (dst);
	}
	else
	{
		i = len - 1;
		while (i >= 0)
		{
			*(unsigned char *)(dst + i) = *(unsigned char *)(src + i);
			i--;
		}
		return (dst);
	}
}
// #include <stdio.h>
// #include <string.h>
// #include "libft.h"
// int	main(void)
// {
// 	char	s1[20] = "123456789";
// 	char	s2[20] = "123456789";
// 	ft_memmove(s1 + 2, s1, 5);
// 	memmove(s2 + 2, s2, 5);
// 	printf("ft_memmove: %s\n", s1);
// 	printf("   memmove: %s\n", s2);
// 	return (0);
// }
