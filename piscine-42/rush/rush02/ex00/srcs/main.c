/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: ppeuvrel <ppeuvrel@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/14 12:09:22 by ppeuvrel          #+#    #+#             */
/*   Updated: 2025/12/14 12:09:33 by ppeuvrel         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_h.h"

int	gest_argv(int argc, char **argv, char **nb, char **dictpath)
{
	if (argc == 2)
	{
		*dictpath = "dicts/numbers.dict";
		*nb = argv[1];
		return (1);
	}
	else if (argc == 3)
	{
		*dictpath = argv[1];
		*nb = argv[2];
		return (1);
	}
	return (0);
}

int	test_nb(char *nb)
{
	int	i;

	i = -1;
	while (nb[++i])
		if (nb[i] < '0' || nb[i] > '9')
			return (0);
	return (1);
}

int	main(int argc, char **argv)
{
	t_dict	*dict;
	char	*nb;
	char	*dictpath;

	if (gest_argv(argc, argv, &nb, &dictpath) == 0 || test_nb(nb) == 0)
		ft_putstr("Error\n");
	else
	{
		dict = 0;
		if (ft_file_read(dictpath, &dict) == 1)
			check_number(nb, dict);
		else
			ft_putstr("Dict Error\n");
	}
	ft_list_clear(&dict);
	return (0);
}
