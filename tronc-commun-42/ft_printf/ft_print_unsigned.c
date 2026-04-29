/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_print_unsigned.c                                :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/12 15:45:13 by omischle          #+#    #+#             */
/*   Updated: 2026/04/29 17:19:02 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

static int	ft_putchar_count(char c)
{
	if (write(1, &c, 1) < 0)
		return (-1);
	return (1);
}

static int	ft_putunbr_rec(unsigned int n)
{
	int	count;
	int	ret;

	count = 0;
	if (n >= 10)
	{
		ret = ft_putunbr_rec(n / 10);
		if (ret < 0)
			return (-1);
		count += ret;
	}
	ret = ft_putchar_count((char)((n % 10) + '0'));
	if (ret < 0)
		return (-1);
	count += ret;
	return (count);
}

int	ft_print_unsigned(unsigned int n)
{
	return (ft_putunbr_rec(n));
}
