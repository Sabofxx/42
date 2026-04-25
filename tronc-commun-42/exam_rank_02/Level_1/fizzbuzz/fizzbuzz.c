/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   fizzbuzz.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: alex <alex@student.42.fr>                  +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/03/15 14:07:53 by alex              #+#    #+#             */
/*   Updated: 2024/03/16 16:26:02 by alex             ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>

void	put_num(int n)
{
	char	*decimal;

	decimal = "0123456789";
	if (n > 9)
		put_num(n / 10);
	write(1, &decimal[n % 10], 1);
}

void	fizzbuzz(int len)
{
	int	i;

	i = 1;
	while (i < len)
	{
		if (i % 15 == 0)
			write(1, "fizzbuzz", 8);
		else if (i % 3 == 0)
			write(1, "fizz", 4);
		else if (i % 5 == 0)
			write(1, "buzz", 4);
		else
			put_num(i);
		i++;
		write(1, "\n", 1);
	}
}

int	main(void)
{
	fizzbuzz(101);
	return (0);
}
