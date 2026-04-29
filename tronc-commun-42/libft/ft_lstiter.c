/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_lstiter.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/15 18:00:03 by omischle          #+#    #+#             */
/*   Updated: 2026/01/15 18:00:11 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	ft_lstiter(t_list *lst, void (*f)(void *))
{
	if (!f)
		return ;
	while (lst)
	{
		f(lst->content);
		lst = lst->next;
	}
}
// #include <stdio.h>
// static void	print_int(void *p)
// {
// 	printf("%d\n", *(int *)p);
// }
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
// 	ft_lstiter(lst, print_int);
// 	return (0);
// }