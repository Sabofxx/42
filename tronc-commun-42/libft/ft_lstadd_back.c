/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_lstadd_back.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/15 17:56:18 by omischle           #+#    #+#             */
/*   Updated: 2026/01/15 17:56:32 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	ft_lstadd_back(t_list **lst, t_list *new)
{
	t_list	*last;

	if (!lst || !new)
		return ;
	if (!*lst)
	{
		*lst = new;
		return ;
	}
	last = ft_lstlast(*lst);
	last->next = new;
}
// #include <stdio.h>
// int	main(void)
// {
// 	t_list *lst;
// 	int a = 1;
// 	int b = 2;
// 	int c = 3;
// 	lst = NULL;
// 	ft_lstadd_back(&lst, ft_lstnew(&a));
// 	ft_lstadd_back(&lst, ft_lstnew(&b));
// 	ft_lstadd_back(&lst, ft_lstnew(&c));
// 	printf("%d\n", *(int *)lst->content);
// 	printf("%d\n", *(int *)lst->next->content);
// 	printf("%d\n", *(int *)lst->next->next->content);
// 	return (0);
// }