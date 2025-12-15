/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_range.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/14 14:27:04 by omischle          #+#    #+#             */
/*   Updated: 2025/12/14 15:10:58 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdlib.h>
#include <stdio.h>

int	*ft_range(int min, int max)
{
	int	*jsp;
	int	*jsp1;

	if (min >= max)
		return (0);
	jsp = (int *)malloc(sizeof(int) * ((long long)max - min));
	if (!jsp)
		return (0);
	jsp1 = jsp;
	while (min < max)
	{
		*(jsp1++) = min++;
	}
	return (jsp);
}

/*int main ()
{
	int min = 213;
	int max = 789;

	int *tab = ft_range(min, max);
	printf("%d\n", tab[0]);
	printf("%d\n", tab[575]);
	free(tab);
}*/
