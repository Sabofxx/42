/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_itoa.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/15 15:42:08 by omischle           #+#    #+#             */
/*   Updated: 2026/01/19 19:12:23 by omischle            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static size_t	ft_nbrlen(long n)
{
	size_t	len;

	len = 1;
	if (n < 0)
		n = -n;
	while (n >= 10)
	{
		n /= 10;
		len++;
	}
	return (len);
}

static void	ft_fill_itoa(char *s, long nb, size_t len, int neg)
{
	s[len] = '\0';
	if (neg)
		s[0] = '-';
	while (len > (size_t)neg)
	{
		len--;
		s[len] = (nb % 10) + '0';
		nb /= 10;
	}
}

char	*ft_itoa(int n)
{
	long	nb;
	size_t	len;
	char	*s;
	int		neg;

	nb = (long)n;
	neg = (nb < 0);
	if (neg)
		nb = -nb;
	len = ft_nbrlen((long)n) + (size_t)neg;
	s = (char *)malloc(len + 1);
	if (!s)
		return (NULL);
	ft_fill_itoa(s, nb, len, neg);
	return (s);
}
// #include <stdio.h>
// int	main(void)
// {
// 	char *s;
// 	s = ft_itoa(-2147483648);
// 	printf("%s\n", s);
// 	free(s);
// 	s = ft_itoa(0);
// 	printf("%s\n", s);
// 	free(s);
// 	return (0);
// }
