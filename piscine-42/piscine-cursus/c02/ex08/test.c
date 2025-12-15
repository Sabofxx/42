/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   test.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/03 11:55:42 by omischle          #+#    #+#             */
/*   Updated: 2025/12/03 12:11:42 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

char *ft_strlowcase(char *str)
{
	int i;
	i = 0;

	while (str[i] != 0)
	{
		if (str[i] >= 'A' && str[i] <='Z')
		{
			str [i] = str[i] + 32;
		}
		i++;
	}
	return (str);
}



int main ()
{
	char str1 [] = "Driss";
	char str2 [] = "BOUBOU";

	printf ("avant : %s  ", str1);
	printf ("apres : %s  ", ft_strlowcase(str1));
	printf ("avant : %s  ", str2);
	printf ("apres : %s\n", ft_strlowcase(str2));
}
