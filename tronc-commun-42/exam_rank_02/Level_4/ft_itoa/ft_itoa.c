/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_itoa.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: alex <alex@student.42.fr>                  +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/04/26 12:29:20 by alex              #+#    #+#             */
/*   Updated: 2024/04/26 15:15:54 by alex             ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

/* #include <stdio.h>
#include <stdlib.h>
 */
int	len_int(int nbr)
{
	int	len;

	len = 0;
	if (nbr == 0)
		return (1);
	if (nbr < 0)
	{
		len++;
		nbr = -nbr;
	}
	while (nbr)
	{
		nbr /= 10;
		len++;
	}
	return (len);
}

char	*ft_itoa(int nbr)
{
	int		len;
	char	*result;

	if (nbr == -2147483648)
		return ("-2147483648");
	len = len_int(nbr) + 1;
	result = malloc(len * sizeof(char));
	if (result == NULL)
		return (NULL);
	result[len] = '\0';
	len--;
	if (nbr == 0)
	{
		result[0] = '0';
		return (result);
	}
	if (nbr < 0)
	{
		result[0] = '-';
		nbr = -nbr;
	}
	while (nbr)
	{
		result[--len] = nbr % 10 + '0';
		nbr /= 10;
	}
	if (nbr > 0)
		result[0] = nbr % 10 + '0';
	return (result);
}

/* int	main(void)
{
	printf("%s", ft_itoa(-98765));
}
 */