/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_lstdelone.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/15 17:57:06 by omischle           #+#    #+#             */
/*   Updated: 2026/01/15 17:58:02 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	ft_lstdelone(t_list *lst, void (*del)(void *))
{
	if (!lst || !del)
		return ;
	del(lst->content);
	free(lst);
}
// #include <stdio.h>
// static void	del_int(void *p)
// {
// 	(void)p;
// }
// int	main(void)
// {
// 	t_list *n;
// 	int a = 42;
// 	n = ft_lstnew(&a);
// 	ft_lstdelone(n, del_int);
// 	return (0);
// }