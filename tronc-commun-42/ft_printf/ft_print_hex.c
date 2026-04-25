/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_print_hex.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/12 15:44:59 by omischle           #+#    #+#             */
/*   Updated: 2026/02/12 15:46:40 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

static int	ft_putchar_count(char c)
{
	if (write(1, &c, 1) < 0)
		return (-1);
	return (1);
}

static int	ft_puthex_rec(unsigned long n, int uppercase)
{
	char	*base;
	int		count;
	int		ret;

	if (uppercase)
		base = "0123456789ABCDEF";
	else
		base = "0123456789abcdef";
	count = 0;
	if (n >= 16)
	{
		ret = ft_puthex_rec(n / 16, uppercase);
		if (ret < 0)
			return (-1);
		count += ret;
	}
	ret = ft_putchar_count(base[n % 16]);
	if (ret < 0)
		return (-1);
	count += ret;
	return (count);
}

int	ft_print_hex(unsigned long n, int uppercase)
{
	return (ft_puthex_rec(n, uppercase));
}
