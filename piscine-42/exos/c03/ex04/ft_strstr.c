/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strstr.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/03 13:11:18 by omischle          #+#    #+#             */
/*   Updated: 2025/12/05 17:29:59 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>
#include <string.h>

char	*ft_strstr(char *str, char *to_find)
{
	int	i;
	int	j;

	if (to_find[0] == '\0')
		return (str);
	i = 0;
	while (str[i])
	{
		j = 0;
		while (str[i + j] == to_find[j] && to_find[j] != '\0')
		{
			if (to_find[j + 1] == '\0')
				return (&str[i]);
			j++;
		}
		i++;
	}
	return (0);
}

/*
int	main(void)
{
	char	str[] = "trouve driss boubou je taime";
	char	to_find[] = "d";
	char	str1[] = "trouve driss boubou je taime";
	char	to_find1[] = "d";

	printf("Return de ma fonction : %s\n", ft_strstr(str, to_find));
	printf("Return de la fonction : %s\n", strstr(str1, to_find1));
}
*/
