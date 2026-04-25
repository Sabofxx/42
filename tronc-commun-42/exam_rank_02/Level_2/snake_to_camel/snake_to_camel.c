/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   snake_to_camel.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: columbux <columbux@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/04/30 17:21:26 by columbux          #+#    #+#             */
/*   Updated: 2024/04/30 19:28:26 by columbux         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>

void	snake_to_camel(char *str)
{
	char	c;
	int		i;

	i = 0;
	while (str[i++] != '\0')
	{
		if (str[i] == '_')
		{
			i++;
			c = str[i] - 32;
			write(1, &c, 1);
		}
		else
			write(1, &str[i], 1);
	}
}

int	main(int ac, char **av)
{
	if (ac == 2)
		snake_to_camel(av[1]);
	write(1, "\n", 1);
	return (0);
}
