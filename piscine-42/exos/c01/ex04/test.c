/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   test.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 15:47:48 by omischle          #+#    #+#             */
/*   Updated: 2025/12/04 15:55:10 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>


void ft_ultimate_div_mod(int *a, int *b)
{
	int mod;
	int div;

	div = (*a / *b);
	mod = (*a % *b);

	*a = div;
	*b = mod;
}

int main()
{
	int a = 20 ;
	int b = 10 ;

	ft_ultimate_div_mod(&a, &b);
	printf("div : %d\n", a);
	printf("mod : %d\n", b);
}
