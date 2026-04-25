/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strchr.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/14 16:10:38 by omischle           #+#    #+#             */
/*   Updated: 2026/01/14 18:41:57 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strchr(const char *s, int c)
{
	unsigned char	ch;

	ch = (unsigned char)c;
	while (*s)
	{
		if ((unsigned char)*s == ch)
			return ((char *)s);
		s++;
	}
	if (ch == '\0')
		return ((char *)s);
	return (NULL);
}
// #include <stdio.h>
// #include <string.h>
// int	main(void)
// {
// 	char	str[] = "driss lktf";
// 	char	*res1;
// 	char	*res2
// 	res1 = ft_strchr(str, 'o');
// 	res2 = strchr(str, 'o');
// 	printf("ft_strchr: %s\n", res1);
// 	printf("   strchr: %s\n", res2);
// 	res1 = ft_strchr(str, 'z');
// 	res2 = strchr(str, 'z');
// 	printf("ft_strchr (not found): %p\n", res1);
// 	printf("   strchr (not found): %p\n", res2);
// 	return (0);
// }
