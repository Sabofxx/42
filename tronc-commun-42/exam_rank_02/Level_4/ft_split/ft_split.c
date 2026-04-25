/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_split.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: columbux <columbux@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/03/21 16:58:50 by columbux          #+#    #+#             */
/*   Updated: 2024/03/21 17:27:35 by columbux         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdlib.h>

int	ft_strlen(char *str)
{
	int	len;

	len = 0;
	while (str[len] != '\0')
		len++;
	return (len);
}

char	**ft_split(char *str)
{
	char	**split;
	int		i;
	int		j;
	int		k;

	i = 0;
	j = 0;
	k = 0;
	split = (char **)malloc(sizeof(char *) * (ft_strlen(str) + 1));
	while (str[i] != '\0')
	{
		while (str[i] != ' ')
		{
			split[j][k] = str[i];
			i++;
			k++;
		}
		split[j][k] = '\0';
		j++;
		if (str[i] == ' ')
			i++;
	}
	split[j] = NULL;
	return (split);
}
