/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   test2.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 16:19:04 by omischle          #+#    #+#             */
/*   Updated: 2025/12/04 16:24:43 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

char *ft_strncpy(char *dest, char *src, unsigned int n)
{
	unsigned int i;
	i = 0;
	
	while(src[i] != '\0' && i < n)
	{
		dest[i] = src[i];
		i++;
	}
	while(i < n)
	{
		dest[i] = 0;
		i++;
	}
	return(dest);
}

int	main(void)
{
	char	dest[] = "Dest";
	char	src[] = "Source";
	int		n;

	n = 6;
	printf("Avant copie : dest = \"%s\"\n", dest);
	ft_strncpy(dest, src, n);
	printf("Apres copie : dest = \"%s\"\n", dest);
	return (0);
}

