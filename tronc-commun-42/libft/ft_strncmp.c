/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strncmp.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/14 16:10:19 by omischle          #+#    #+#             */
/*   Updated: 2026/01/14 16:10:23 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

int	ft_strncmp(const char *s1, const char *s2, size_t n)
{
	size_t	i;

	i = 0;
	while (i < n && s1[i] && s2[i] && s1[i] == s2[i])
		i++;
	if (i == n)
		return (0);
	return ((unsigned char)s1[i] - (unsigned char)s2[i]);
}
// #include <stdio.h>
// #include <string.h>
// int	main(void)
// {
// 	char a[] = "oscar";
// 	char b[] = "oscar123";
// 	printf("%d\n", ft_strncmp(a, b, 5));
// 	printf("%d\n", strncmp(a, b, 5));
// 	printf("%d\n", ft_strncmp(a, b, 7));
// 	printf("%d\n", strncmp(a, b, 7));
// 	return (0);
// }