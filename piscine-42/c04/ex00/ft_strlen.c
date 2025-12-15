/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strlen.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 17:29:04 by omischle          #+#    #+#             */
/*   Updated: 2025/12/04 17:34:27 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

int	ft_strlen(char *str)
{
	int	driss;

	driss = 0;
	while (str[driss])
	{
		driss++;
	}
	return (driss);
}

/*
int	main(void)
{
	char	str[] = "ihefoih";

	printf("%d\n", ft_strlen(str));
}
*/
