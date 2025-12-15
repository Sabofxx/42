/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   checks_number.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: ppeuvrel <ppeuvrel@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/14 12:03:43 by ppeuvrel          #+#    #+#             */
/*   Updated: 2025/12/14 16:58:17 by ppeuvrel         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_h.h"
#include "ft_h.h"

t_dict	*find_dict_entry(int nb_to_find, int is_suffix, t_dict *begin_list)
{
	t_dict	*current;

	current = begin_list;
	while (current != NULL)
	{
		if (current->suf == is_suffix && current->nb == nb_to_find)
			return (current);
		current = current->next;
	}
	return (NULL);
}

int	check_length(char *nbr)
{
	int	i;
	int	j;

	i = 0;
	j = 0;
	while (nbr[j] == '0')
		j++;
	while (nbr[i + j])
	{
		i++;
	}
	return (i);
}

void	check_and(int nb, int i, char *nbr)
{
	int	j;

	j = 0;
	if (nb != 0)
	{
		while (nbr[j] == '0' && j < i)
			j++;
		if ((i - j) > 2 && (nb % 100 != 0) && check_length(nbr) > 2 && (nb
				/ 100 >= 1 || i == check_length(nbr)))
			ft_putstr("and ");
	}
}
