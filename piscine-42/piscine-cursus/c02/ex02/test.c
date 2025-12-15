/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   test.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/03 12:48:36 by omischle          #+#    #+#             */
/*   Updated: 2025/12/03 12:57:14 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

int ft_str_is_alpha(char *str)
{
	int i;
	i = 0;

	while (str[i] != '\0')
	{
		if (!((str [i] >= 'a') && (str [i] <= 'z') 
				|| (str[i] >= 'A') && (str[i] <= 'Z')))
			return (0);
		i++;
	}
	return (1);
}


int	main(void)
{
	char	str1[] = "Hello";
	char	str2[] = "iweobhfoiwefbh0-148";

	printf("%s is alpha? %d\n", str1, ft_str_is_alpha(str1));
	printf("%s is alpha? %d\n", str2, ft_str_is_alpha(str2));
	return (0);
}
