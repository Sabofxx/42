/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   split_number.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: ppeuvrel <ppeuvrel@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/14 12:10:39 by ppeuvrel          #+#    #+#             */
/*   Updated: 2025/12/14 16:50:52 by ppeuvrel         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_h.h"

int	first_check(char *nbr, int *i, int *j, t_dict *begin_list)
{
	int		k;
	int		nb;
	char	nbr2[20];

	k = 0;
	while (nbr[*i] == '0')
		(*i)++;
	if (*j % 3 != 0)
	{
		while (*j % 3 != 0 || *j == 0)
		{
			nbr2[k++] = nbr[(*i)++];
			(*j)--;
		}
		nbr2[k] = '\0';
		send_to_print((nb = ft_atoi(nbr2)), begin_list, *i, nbr);
		if (*j == 0)
		{
			ft_putchar('\n');
			return (0);
		}
		if (*j >= 3)
			print_suff(*i, nbr, *j / 3, begin_list);
	}
	return (1);
}

void	make_three(int i, int j, char *nbr, t_dict *begin_list)
{
	int		nb;
	int		k;
	char	nbr2[10];

	while (j > 0)
	{
		k = 0;
		while (k != 3)
		{
			nbr2[k] = nbr[i];
			i++;
			j--;
			k++;
		}
		nbr2[k] = '\0';
		nb = ft_atoi(nbr2);
		if (nb != 0)
		{
			send_to_print(nb, begin_list, i, nbr);
			if (j >= 3)
				print_suff(i, nbr, j / 3, begin_list);
		}
	}
}

int	check_number(char *nbr, t_dict *begin_list)
{
	int	i;
	int	j;

	i = 0;
	j = check_length(nbr);
	if (j > 3 && find_dict_entry((j - 1) / 3, 1, begin_list) == NULL)
		return (0);
	if (ft_atoi(nbr) == 0)
	{
		ft_putstr("zero");
		ft_putchar('\n');
		return (0);
	}
	if (first_check(nbr, &i, &j, begin_list) == 0)
		return (0);
	make_three(i, j, nbr, begin_list);
	ft_putchar('\n');
	return (0);
}
