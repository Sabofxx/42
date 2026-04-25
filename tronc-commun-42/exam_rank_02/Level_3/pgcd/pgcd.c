/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   pgcd.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: alex <alex@student.42.fr>                  +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/04/15 15:20:30 by alex              #+#    #+#             */
/*   Updated: 2024/04/17 13:23:31 by alex             ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdlib.h>
#include <stdio.h>

void	pgcd(int a, int b)
{
	int	result;
	int	div;

	if (a < 0 || b < 0)
		return ;
	div = 1;
	result = 0;
	while (div <= a && div <= b)
	{
		if (a % div == 0 && b % div == 0)
			result = div;
		div++;
	}
	printf("%d", result);
}

int	main(int argc, char **argv)
{
	if (argc == 3)
		pgcd(atoi(argv[1]), atoi(argv[2]));
	printf("\n");
	return (0);
}
