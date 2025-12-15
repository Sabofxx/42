/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strcpy.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/01 10:43:38 by omischle          #+#    #+#             */
/*   Updated: 2025/12/09 08:50:37 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

char	*ft_strcpy(char *dest, char *src)
{
	int	i;

	i = 0;
	while (src[i])
	{
		dest[i] = src[i];
		i++;
	}
	dest[i] = src[i];
	return (dest);
}

int	main(void)
{
	char	dest [] = "";
	char	src[] = "Source";

	printf("Avant copie : dest = \"%s\"\n", dest);
	
	ft_strcpy(dest, src);

	printf("Apres copie : dest = \"%s\"\n", dest);
	return (0);
}
