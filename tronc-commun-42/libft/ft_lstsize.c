/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_lstsize.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/15 17:53:15 by omischle           #+#    #+#             */
/*   Updated: 2026/01/15 17:54:42 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

int	ft_lstsize(t_list *lst)
{
	int	count;

	count = 0;
	while (lst)
	{
		count++;
		lst = lst->next;
	}
	return (count);
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
// 	printf("%d\n", ft_lstsize(lst));
// 	return (0);
// }