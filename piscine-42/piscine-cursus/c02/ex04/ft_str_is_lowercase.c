/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_str_is_lowercase.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/01 16:40:25 by omischle          #+#    #+#             */
/*   Updated: 2025/12/01 16:42:38 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

int	ft_str_is_lowercase(char *str)
{
	int	i;

	i = 0;
	while (str[i] != 0)
	{
		if (!((str[i] >= 'a' && str[i] <= 'z')))
		{
			return (0);
		}
		i++;
	}
	return (1);
}

/*
int	main(void)
{
	char	str1[] = "hello";
	char	str2[] = "Hel lo";

	printf("%s is alpha? %d\n", str1, ft_str_is_lowercase(str1));
	printf("%s is alpha? %d\n", str2, ft_str_is_lowercase(str2));
	return (0);
}
*/
