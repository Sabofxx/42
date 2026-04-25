/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_lstclear.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/15 17:58:46 by omischle           #+#    #+#             */
/*   Updated: 2026/01/15 17:59:14 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	ft_lstclear(t_list **lst, void (*del)(void *))
{
	t_list	*tmp;

	if (!lst || !del)
		return ;
	while (*lst)
	{
		tmp = (*lst)->next;
		del((*lst)->content);
		free(*lst);
		*lst = tmp;
	}
}
// #include <stdio.h>
// static void	del_int(void *p)
// {
// 	(void)p;
// }
// int	main(void)
// {
// 	t_list *lst;
// 	int a = 1;
// 	int b = 2;
// 	lst = NULL;
// 	ft_lstadd_front(&lst, ft_lstnew(&a));
// 	ft_lstadd_front(&lst, ft_lstnew(&b));
// 	ft_lstclear(&lst, del_int);
// 	if (!lst)
// 		printf("list cleared\n");
// 	return (0);
// }