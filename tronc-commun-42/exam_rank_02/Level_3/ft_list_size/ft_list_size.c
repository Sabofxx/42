/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_list_size.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>                  +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/04/19 17:58:32 by omischle              #+#    #+#             */
/*   Updated: 2024/04/21 18:18:46 by omischle             ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_list_size.h"

int	ft_list_size(t_list *begin_list)
{
	int		len;

	len = 0;
	while (begin_list != NULL)
	{
		len++;
		begin_list = begin_list->next;
	}
	return (len);
}
