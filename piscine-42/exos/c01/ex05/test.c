/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   test.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 15:55:57 by omischle          #+#    #+#             */
/*   Updated: 2025/12/04 16:01:36 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>

void ft_putchar(char c)
{
	write(1, &c, 1);
}

void ft_putstr(char *str)
{
	int prout;
	prout = 0;

	while (str[prout] != '\0')
	{	
		ft_putchar(str[prout]);
		prout++;
	}
}

int main ()
{
	char	str1[] = "Hello";

	ft_putstr(str1);
	ft_putchar('\n');
}

