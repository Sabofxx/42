/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_recursive_factorial.c                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/08 12:24:10 by omischle          #+#    #+#             */
/*   Updated: 2025/12/10 12:53:41 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

int	ft_recursive_factorial(int nb)
{
	if (nb < 0)
		return (0);
	else if (nb == 0)
		return (1);
	else if (nb == 1)
		return (nb);
	else
		return (nb * ft_recursive_factorial(nb - 1));
}

/*
int	main(int ac,char **av)
{
	printf("%d\n", ft_recursive_factorial(12));
}
*/
