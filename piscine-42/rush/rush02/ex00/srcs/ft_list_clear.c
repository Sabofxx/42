/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_list_clear.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: ppeuvrel <ppeuvrel@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/14 12:06:29 by ppeuvrel          #+#    #+#             */
/*   Updated: 2025/12/14 17:05:33 by ppeuvrel         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_h.h"

void	ft_list_clear(t_dict **begin_with)
{
	t_dict	*ptr;
	t_dict	*liste;

	liste = *begin_with;
	if (liste)
	{
		while (liste)
		{
			ptr = liste->next;
			free(liste);
			liste = ptr;
		}
	}
}
