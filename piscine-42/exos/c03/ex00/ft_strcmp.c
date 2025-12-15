/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strcmp.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/02 11:26:28 by omischle          #+#    #+#             */
/*   Updated: 2025/12/04 13:49:57 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

int	ft_strcmp(char *s1, char *s2)
{
	int	i;

	i = 0;
	while (s1[i] == s2[i] && s1[i] != '\0')
	{
		i++;
	}
	return (s1[i] - s2[i]);
}

/*
int	main(void)
{
	char	*s1;
	char	*s2;

	s1 = "driss";
	s2 = "9riss";
	printf("diff : %d\n", ft_strcmp(s1, s2));
	return (0);
}
*/
