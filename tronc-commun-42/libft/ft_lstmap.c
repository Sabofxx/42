/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_lstmap.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/15 18:00:42 by omischle          #+#    #+#             */
/*   Updated: 2026/01/15 18:00:56 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

t_list	*ft_lstmap(t_list *lst, void *(*f)(void *), void (*del)(void *))
{
	t_list	*new_lst;
	t_list	*new_node;
	void	*new_content;

	if (!f || !del)
		return (NULL);
	new_lst = NULL;
	while (lst)
	{
		new_content = f(lst->content);
		new_node = ft_lstnew(new_content);
		if (!new_node)
		{
			del(new_content);
			ft_lstclear(&new_lst, del);
			return (NULL);
		}
		ft_lstadd_back(&new_lst, new_node);
		lst = lst->next;
	}
	return (new_lst);
}
// #include <stdio.h>
// static void	*double_int(void *p)
// {
// 	int *n;
// 	n = malloc(sizeof(int));
// 	if (!n)
// 		return (NULL);
// 	*n = (*(int *)p) * 2;
// 	return (n);
// }
// static void	del_int(void *p)
// {
// 	free(p);
// }
// int	main(void)
// {
// 	t_list *lst;
// 	t_list *new;
// 	int a = 1;
// 	int b = 2;
// 	lst = NULL;
// 	ft_lstadd_front(&lst, ft_lstnew(&a));
// 	ft_lstadd_front(&lst, ft_lstnew(&b));
// 	new = ft_lstmap(lst, double_int, del_int);
// 	while (new)
// 	{
// 		printf("%d\n", *(int *)new->content);
// 		new = new->next;
// 	}
// 	return (0);
// }