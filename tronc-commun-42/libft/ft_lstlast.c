/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_lstlast.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/15 17:55:17 by omischle          #+#    #+#             */
/*   Updated: 2026/01/15 17:55:49 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

t_list	*ft_lstlast(t_list *lst)
{
	if (!lst)
		return (NULL);
	while (lst->next)
		lst = lst->next;
	return (lst);
}
// #include <stdio.h>
// int	main(void)
// {
// 	t_list *lst;
// 	int a = 1;
// 	int b = 2;
// 	int c = 3;
// 	lst = NULL;
// 	ft_lstadd_front(&lst, ft_lstnew(&a));
// 	ft_lstadd_front(&lst, ft_lstnew(&b));
// 	ft_lstadd_front(&lst, ft_lstnew(&c));
// 	printf("%d\n", *(int *)ft_lstlast(lst)->content);
// 	return (0);
// }