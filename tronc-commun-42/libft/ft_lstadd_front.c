/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_lstadd_front.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/15 17:51:10 by omischle           #+#    #+#             */
/*   Updated: 2026/01/15 17:52:25 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	ft_lstadd_front(t_list **lst, t_list *new)
{
	if (!lst || !new)
		return ;
	new->next = *lst;
	*lst = new;
}
// #include <stdio.h>
// int	main(void)
// {
// 	t_list *lst;
// 	t_list *n1;
// 	t_list *n2;
// 	int a = 1;
// 	int b = 2;
// 	lst = NULL;
// 	n1 = ft_lstnew(&a);
// 	n2 = ft_lstnew(&b);
// 	ft_lstadd_front(&lst, n1);
// 	ft_lstadd_front(&lst, n2);
// 	printf("%d\n", *(int *)lst->content);
// 	printf("%d\n", *(int *)lst->next->content);
// 	free(n1);
// 	free(n2);
// 	return (0);
// }