/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strlcat.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 17:22:03 by omischle          #+#    #+#             */
/*   Updated: 2025/12/08 14:23:06 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <string.h>

unsigned int	ft_strlcat(char *dest, char *src, unsigned int size)
{
	unsigned int	longdest;
	unsigned int	longsrc;
	unsigned int	i;

	longdest = 0;
	longsrc = 0;
	while (dest[longdest] != '\0')
		longdest++;
	while (src[longsrc] != '\0')
		longsrc++;
	if (size <= longdest)
		return (size + longsrc);
	i = 0;
	while (src[i] != '\0' && longdest + i < size - 1)
	{
		dest[longdest + i] = src[i];
		i++;
	}
	dest[longdest + i] = '\0';
	return (longdest + longsrc);
}

/*
#include <stdio.h>
#include <string.h>

unsigned int	ft_strlcat(char *dest, char *src, unsigned int size);

int main ()
{
	char d1[20] = "Hello";
	printf("%u | %s\n", ft_strlcat(d1, " World", 20), d1);
}
*/
