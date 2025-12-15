/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_show_tab.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: colassin <colassin@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/11 19:18:11 by colassin          #+#    #+#             */
/*   Updated: 2025/12/12 10:30:21 by colassin         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_stock_str.h"
#include <unistd.h>

void	ft_putstr(char *str)
{
	int	i;

	i = 0;
	while (str[i])
	{
		write(1, &str[i], 1);
		i++;
	}
}

void	ft_putchar(char c)
{
	write(1, &c, 1);
}

void	ft_putnbr(int nb)
{
	long int	nbr;

	nbr = nb;
	if (nbr < 0)
	{
		ft_putchar('-');
		nbr *= -1;
	}
	if (nbr > 9)
	{
		ft_putnbr(nbr / 10);
		ft_putnbr(nbr % 10);
	}
	if (nbr >= 0 && nbr <= 9)
	{
		ft_putchar(nbr + '0');
	}
}

void	ft_show_tab(struct s_stock_str *par)
{
	int	i;

	i = 0;
	while (par[i].str)
	{
		ft_putstr(par[i].str);
		write(1, "\n", 1);
		ft_putnbr(par[i].size);
		write(1, "\n", 1);
		ft_putstr(par[i].copy);
		write(1, "\n", 1);
		i++;
	}
}
/*
int	main(void)
{
	char *strings[] = {"Hello", "World", "42", "Test"};
	t_stock_str *result;
	int i;

	result = ft_strs_to_tab(4, strings);

	if (!result)
	{
		//printf("Error: malloc failed\n");
		return (1);
	}
	ft_show_tab(result);
} */