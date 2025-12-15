/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_iterative_power.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/08 13:06:25 by omischle          #+#    #+#             */
/*   Updated: 2025/12/08 13:29:31 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

int	ft_iterative_power(int nb, int power)
{
	int	result;

	if (power < 0)
		return (0);
	else if (power == 0)
		return (1);
	else
	{
		result = nb;
		while (power != 1)
		{
			result = result * nb;
			power--;
		}
		return (result);
	}
}

/*
int	main(void)
{
	printf("%d\n", ft_iterative_power(15, 5));
}
*/
