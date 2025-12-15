/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_str_is_printable.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/01 16:47:25 by omischle          #+#    #+#             */
/*   Updated: 2025/12/01 18:10:43 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

int	ft_str_is_printable(char *str)
{
	int	i;

	i = 0;
	while (str[i] != 0)
	{
		if (!((str[i] >= ' ' && str[i] <= '~')))
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
	char	str1[] = "DrissBOUBOU9017361240987 pjhfop!@)#*";
	char	str2[] = "Hel lo";

	printf("%s is alpha? %d\n", str1, ft_str_is_printable(str1));
	printf("%s is alpha? %d\n", str2, ft_str_is_printable(str2));
	return (0);
}
*/
