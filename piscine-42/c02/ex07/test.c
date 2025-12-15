/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   test.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/03 12:13:08 by omischle          #+#    #+#             */
/*   Updated: 2025/12/03 12:22:09 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

char *ft_strupcase(char *str)
{
	int i;
	i = 0;

	while (str[i] != 0)
	{
		if (str[i] >= 'a' && str[i] <= 'z')
		{
			str [i] = str [i] - 32;
		}
		i++;
	}
	return (str);
}

int main ()
{
	char str1 [] = "driss";
	char str2 [] = "BouBOUeoikfh";

	printf("avant : %s ", str1);
	printf("apres : %s ", ft_strupcase(str1));
	printf("avant : %s ", str2);
	printf("apres : %s ", ft_strupcase(str2));
}
