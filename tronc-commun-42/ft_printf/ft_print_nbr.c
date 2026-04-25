/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_print_nbr.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/12 15:45:02 by omischle           #+#    #+#             */
/*   Updated: 2026/02/12 15:46:43 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

static int	ft_putchar_count(char c)
{
	if (write(1, &c, 1) < 0)
		return (-1);
	return (1);
}

static int	ft_putnbr_rec(long n)
{
	int	count;
	int	ret;

	count = 0;
	if (n >= 10)
	{
		ret = ft_putnbr_rec(n / 10);
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

int	ft_print_nbr(int n)
{
	long	nb;
	int		count;
	int		ret;

	nb = (long)n;
	count = 0;
	if (nb < 0)
	{
		ret = ft_putchar_count('-');
		if (ret < 0)
			return (-1);
		count += ret;
		nb = -nb;
	}
	ret = ft_putnbr_rec(nb);
	if (ret < 0)
		return (-1);
	count += ret;
	return (count);
}
