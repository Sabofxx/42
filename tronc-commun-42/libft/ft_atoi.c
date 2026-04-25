/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_atoi.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 11:46:42 by omischle           #+#    #+#             */
/*   Updated: 2026/01/13 14:21:37 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

int	ft_atoi(const char *str)
{
	int	i;
	int	sign;
	int	r;

	i = 0;
	sign = 1;
	r = 0;
	while (((str[i] >= 9) && (str[i] <= 13)) || (str[i] == 32))
		i++;
	if ((str[i] == '-') || (str[i] == '+'))
	{
		if (str[i] == '-')
		{
			sign = -sign;
		}
		i++;
	}
	while ((str[i] >= '0') && (str[i] <= '9'))
	{
		r = r * 10 + (str[i] - '0');
		i++;
	}
	return (r * sign);
}
// #include <stdio.h>
// int	main(void)
// {
// 	char	str[] = "		-1234ab567";
// 	printf("%d", ft_atoi(str));
// 	return (0);
// }
