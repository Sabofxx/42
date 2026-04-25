/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   last_word.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: alex <alex@student.42.fr>                  +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/04/30 20:24:22 by columbux          #+#    #+#             */
/*   Updated: 2024/05/16 16:06:08 by alex             ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>

void	last_word(char *str)
{
	int	i;

	i = 0;
	while (str[i] != '\0')
		i++;
	i -= 1;
	if (str[i] == ' ' || str[i] == '\t')
	{
		while (str[i] == ' ' || str[i] == '\t')
			--i;
	}
	while (str[i] != ' ' && i > 0)
		i--;
	while (str[i] != '\0')
	{
		if (i == 0)
			write(1, &str[0], 1);
		i++;
		write(1, &str[i], 1);
	}
}

int	main(int argc, char **argv)
{
	if (argc == 2)
		last_word(argv[1]);
	write(1, "\n", 1);
	return (0);
}
