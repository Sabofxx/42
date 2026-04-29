/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_bzero.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 11:46:53 by omischle          #+#    #+#             */
/*   Updated: 2026/01/13 15:22:23 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	ft_bzero(void *s, size_t n)
{
	size_t			i;
	unsigned char	*p;

	p = (unsigned char *)s;
	i = 0;
	while (i < n)
	{
		p[i] = 0;
		i++;
	}
}
// #include <stdio.h>
// int	main(void)
// {
// 	char	s1[10] = "abcde";
// 	int		i;
// 	ft_bzero(s1, 10);
// 	i = 0;
// 	while (i < 10)
// 	{
// 		printf("%d ", s1[i]);
// 		i++;
// 	}
// 	printf("\n");
// 	return (0);
// }