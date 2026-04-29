/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memset.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 11:47:56 by omischle          #+#    #+#             */
/*   Updated: 2026/01/13 16:27:47 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	*ft_memset(void *b, int c, size_t len)
{
	size_t			i;
	unsigned char	*p;

	p = (unsigned char *)b;
	i = 0;
	while (i < len)
	{
		p[i] = (unsigned char)c;
		i++;
	}
	return (b);
}
// #include <stdio.h>
// #include <string.h>
// #include "libft.h"
// int	main(void)
// {
// 	char	a[10];
// 	char	b[10];
// 	ft_memset(a, 'A', 10);
// 	memset(b, 'A', 10);
// 	printf("ft_memset: ");
// 	for (int i = 0; i < 10; i++)
// 		printf("%c", a[i]);
// 	printf("\n");
// 	printf("   memset: ");
// 	for (int i = 0; i < 10; i++)
// 		printf("%c", b[i]);
// 	printf("\n");
// 	return (0);
// }
