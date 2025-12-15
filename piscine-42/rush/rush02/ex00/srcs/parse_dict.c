/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parse_dict.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: ppeuvrel <ppeuvrel@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/14 12:10:02 by ppeuvrel          #+#    #+#             */
/*   Updated: 2025/12/14 17:57:01 by ppeuvrel         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_h.h"
#include <stdlib.h>

int	get_nb(int *nb, int *suf, char *str)
{
	int	i;
	int	j;

	i = 0;
	*nb = 0;
	while (str[i] >= '0' && str[i] <= '9')
		i++;
	if (i >= 4)
	{
		j = -1;
		if ((i - 1) % 3 != 0)
			return (0);
		while (++j < i)
			if ((j == 0 && str[j] != '1') || (j != 0 && str[j] != '0'))
				return (0);
		*nb = i / 3;
		*suf = 1;
	}
	else
		*suf = 0;
	return (1);
}

char	*ft_check_space(char *str)
{
	int		i;
	int		j;
	char	*str2;

	i = -1;
	j = 0;
	while (str[++i])
	{
		if (str[i] != ' ')
			j++;
		else if (str[i - 1] != ' ')
			j++;
	}
	str2 = malloc(sizeof(char) * (j + 1));
	if (str2 == NULL)
		return (NULL);
	i = -1;
	j = 0;
	while (str[++i])
		if (str[i] != ' ' || str[i - 1] != ' ')
			str2[j++] = str[i];
	str2[j] = '\0';
	return (str2);
}

int	test_line(char *str, int *i)
{
	int	j;

	while (str[*i] >= '0' && str[*i] <= '9')
		(*i)++;
	while (str[*i] == ' ')
		(*i)++;
	if (str[*i] != ':')
		return (0);
	(*i)++;
	while (str[*i] == ' ')
		(*i)++;
	j = *i;
	while (str[++j])
		if (str[j] <= 31 || str[j] >= 127)
			return (0);
	return (1);
}

int	handle_entry_addition(t_dict **begin, int nb, int suf, char *str)
{
	t_dict	*tmp;
	int		i;
	char	*str2;

	if (suf == 0)
	{
		tmp = *begin;
		while (tmp)
		{
			if (tmp->nb == nb)
				return (0);
			tmp = tmp->next;
		}
	}
	i = 0;
	if (!test_line(str, &i))
		return (0);
	str2 = ft_strdup(str + i);
	if (!str2)
		return (0);
	str2 = ft_check_space(str2);
	if (!str2)
		return (0);
	return (ft_list_push_front(begin, nb, suf, str2));
}

int	parse_dict(t_dict **begin, char *str)
{
	int		nb;
	int		suf;
	int		atoi_res;

	if (get_nb(&nb, &suf, str) == 0)
		return (0);
	atoi_res = ft_atoi(str);
	if (nb != 0 || atoi_res != -1)
	{
		if (nb == 0)
			nb = atoi_res;
		return (handle_entry_addition(begin, nb, suf, str));
	}
	return (0);
}
