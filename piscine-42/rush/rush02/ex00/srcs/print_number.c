/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   print_number.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: ppeuvrel <ppeuvrel@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/14 12:10:15 by ppeuvrel          #+#    #+#             */
/*   Updated: 2025/12/14 17:54:54 by ppeuvrel         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_h.h"

void	print_nb(int nb, t_dict *begin_list)
{
	t_dict	*entry;

	entry = find_dict_entry(nb, 0, begin_list);
	if (entry == NULL)
		return ;
	ft_putstr(entry->literal);
	if (nb < 20 || nb > 99)
	{
		ft_putchar(' ');
	}
}

void	print_suff(int i, char *nbr, int j, t_dict *begin_list)
{
	t_dict	*entry;

	entry = find_dict_entry(j, 1, begin_list);
	if (entry == NULL)
		return ;
	ft_putstr(entry->literal);
	while (nbr[i] == '0')
		i++;
	if (nbr[i] != '\0' && i != (check_length(nbr) - 1) && i != check_length(nbr)
		- 2)
		ft_putstr(", ");
	if (i == (check_length(nbr) - 1) || i == (check_length(nbr) - 2))
		ft_putchar(' ');
}

void	print_units(int nbr, char *nbrc, int i, t_dict *begin_list)
{
	int	nb;

	if ((nbr % 100) >= 20)
	{
		check_and(nbr, i, nbrc);
		print_nb((nb = (nbr % 100) - (nbr % 10)), begin_list);
		if (nbr % 10 != 0)
		{
			nb = nbr % 10;
			ft_putstr("-");
			print_nb(nb, begin_list);
		}
	}
	else if ((nbr % 100) < 20 && (nbr % 100 != 0))
	{
		print_nb((nb = nbr % 100), begin_list);
	}
}

void	print_hundreds(int nbr, char *nbrc, int i, t_dict *begin_list)
{
	int	nb;

	if ((nbr / 100) > 0)
	{
		nb = nbr / 100;
		print_nb(nb, begin_list);
		print_nb(100, begin_list);
	}
	if (find_dict_entry(nbr % 100, 0, begin_list) != NULL)
	{
		check_and(nbr, i, nbrc);
		print_nb(nbr % 100, begin_list);
		if ((nbr % 100) >= 20)
			ft_putstr(" ");
	}
	else
	{
		print_units(nbr, nbrc, i, begin_list);
	}
}

void	send_to_print(int nbr, t_dict *begin_list, int i, char *nbrc)
{
	int	nb;

	nb = nbr;
	if (find_dict_entry(nb, 0, begin_list) != NULL)
	{
		if (nb == 100)
			ft_putstr("one ");
		check_and(nbr, i, nbrc);
		print_nb(nb, begin_list);
		if (nb >= 20 && nb <= 99)
			ft_putchar(' ');
	}
	else
	{
		print_hundreds(nbr, nbrc, i, begin_list);
	}
}
