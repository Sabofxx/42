/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_create_elem.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: ppeuvrel <ppeuvrel@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/14 12:04:38 by ppeuvrel          #+#    #+#             */
/*   Updated: 2025/12/14 16:14:30 by ppeuvrel         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_h.h"

int	ft_strlen(char *str)
{
	int	i;

	i = 0;
	while (str[i])
		i++;
	return (i);
}

t_dict	*ft_create_elem(int n, int suf, char *literal)
{
	t_dict	*created;

	created = NULL;
	created = malloc(sizeof(t_dict));
	if (created == NULL)
		return (NULL);
	if (created)
	{
		created->nb = n;
		created->suf = suf;
		created->literal = ft_strdup(literal);
		if (created->literal == NULL)
		{
			free(created);
			return (NULL);
		}
		created->next = NULL;
	}
	return (created);
}
