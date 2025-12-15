/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   test.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/03 12:31:43 by omischle          #+#    #+#             */
/*   Updated: 2025/12/03 12:36:11 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

int ft_str_is_uppercase(char *str)
{
	int i;
	i = 0;

	while (str [i] != 0)
	{
		if (!((str[i] >= 'A') && (str[i] <= 'Z')))
		{
			return (0);
		}
		i++;
	}
	return (1);
}

int	main(void)
{
	char	str1[] = "HELLO";
	char	str2[] = "Hel lo";

	printf("%s is alpha? %d\n", str1, ft_str_is_uppercase(str1));
	printf("%s is alpha? %d\n", str2, ft_str_is_uppercase(str2));
	return (0);
}

