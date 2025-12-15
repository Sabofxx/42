/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   test.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 15:21:25 by omischle          #+#    #+#             */
/*   Updated: 2025/12/04 15:25:32 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

char *ft_strcpy(char *dest, char *src)
{
	int i;
	i = 0;

	while(src[i] != '\0')
	{
		dest[i] = src[i];
		i++;
	}
	dest[i] = src[i];
	return (dest);
}

int    main(void)
{
    char    dest[20] = "Dest";
    char    src[] = "Source";

    printf("Avant copie : dest = \"%s\"\n", dest);

    ft_strcpy(dest, src);

    printf("Apres copie : dest = \"%s\"\n", dest);
    return (0);
}
