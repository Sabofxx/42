/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strcmp.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>                  +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/04/17 17:11:22 by omischle              #+#    #+#             */
/*   Updated: 2024/04/21 18:48:55 by omischle             ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

int	ft_strcmp(char *s1, char *s2)
{
	int	i;

	i = 0;
	while (s1[i] == s2[i] && (s1[i] != '\0' || s2[i] != '\0'))
		i++;
	return (s1[i] - s2[i]);
}

/* #include <stdio.h>
#include <string.h>

int	main(int argc, char **argv)
{
	if (argc == 3)
		printf("%d\n", ft_strcmp(argv[1], argv[2]));
	return (0);
} */
