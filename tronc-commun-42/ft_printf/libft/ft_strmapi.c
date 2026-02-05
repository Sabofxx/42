/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strmapi.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/14 15:51:13 by omischle          #+#    #+#             */
/*   Updated: 2026/01/14 20:11:59 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strmapi(char const *s, char (*f)(unsigned int, char))
{
	unsigned int	i;
	char			*res;

	res = malloc((ft_strlen(s) + 1) * sizeof(char));
	if (!res)
		return (NULL);
	i = 0;
	while (i < ft_strlen(s))
	{
		res[i] = (*f)(i, s[i]);
		i++;
	}
	res[i] = 0;
	return (res);
}

/* #include <stdio.h>
#include "libft.h"
#include <stdlib.h>

// ⚡ Déclaration de la fonction avant le main
char	to_uppercase(unsigned int i, char c)
{
	(void)i; // on n'utilise pas l'indice ici
	if (c >= 'a' && c <= 'z')
		return (c - 32); // transforme en majuscule
	return (c);
}

int	main(void)
{
	char	*s;
	char	*res;

	s = "hello world";
	res = ft_strmapi(s, to_uppercase); // utiliser la fonction ici
	if (res == NULL)
	{
		printf("Erreur d'allocation\n");
		return (1);
	}
	printf("Original : %s\n", s);
	printf("Transformée : %s\n", res);
	free(res); // libération de la mémoire
	return (0);
}
 */