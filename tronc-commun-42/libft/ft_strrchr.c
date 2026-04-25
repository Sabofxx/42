/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strrchr.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/14 16:12:03 by omischle           #+#    #+#             */
/*   Updated: 2026/01/14 16:12:04 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strrchr(const char *s, int c)
{
	unsigned char	ch;
	char			*last;

	ch = (unsigned char)c;
	last = NULL;
	while (*s)
	{
		if ((unsigned char)*s == ch)
			last = (char *)s;
		s++;
	}
	if (ch == '\0')
		return ((char *)s);
	return (last);
}
// #include <stdio.h>
// int	main(void)
// {
// 	char str[] = "hello world";
// 	printf("%s\n", ft_strrchr(str, 'o'));
// 	printf("%p\n", ft_strrchr(str, 'z'));
// 	printf("%s\n", ft_strrchr(str, '\0'));
// 	return (0);
// }