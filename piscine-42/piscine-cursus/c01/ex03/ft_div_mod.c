/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_div_mod.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/11/29 15:41:37 by omischle          #+#    #+#             */
/*   Updated: 2025/12/04 15:45:10 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

void	ft_div_mod(int a, int b, int *div, int *mod)
{
	*div = (a / b);
	*mod = (a % b);
}

/*
int	main()
{
	int a = 40;
	int b = 20;
	int mod;
	int div;
	ft_div_mod(a, b, &div, &mod);
	printf("a = %d\n", b);
	printf("b = %d\n", a);
	printf("Divison = %d\n", div);
	printf("Modulo = %d\n", mod);
	return 0;
}
*/
