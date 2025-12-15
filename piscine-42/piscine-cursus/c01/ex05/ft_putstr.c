/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_putstr.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/11/29 17:15:27 by omischle          #+#    #+#             */
/*   Updated: 2025/11/29 17:36:31 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>

void	ft_putchar(char c)
{
	write(1, &c, 1);
}

void	ft_putstr(char *str)
{
	int	cur;

	cur = 0;
	while (str[cur] != 0)
	{
		ft_putchar(str[cur]);
		cur++;
	}
}

/*
int main ()
{
	char	str1[] = "Hello";

	ft_putstr(str1);
	ft_putchar('\n');
}
*/
