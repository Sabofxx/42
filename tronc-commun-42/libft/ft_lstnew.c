/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_lstnew.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/15 17:49:34 by omischle          #+#    #+#             */
/*   Updated: 2026/01/15 17:50:20 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

t_list	*ft_lstnew(void *content)
{
	t_list	*node;

	node = (t_list *)malloc(sizeof(t_list));
	if (!node)
		return (NULL);
	node->content = content;
	node->next = NULL;
	return (node);
}
// #include <stdio.h>
// int	main(void)
// {
// 	t_list *n;
// 	int x = 42;
// 	n = ft_lstnew(&x);
// 	if (!n)
// 		return (1);
// 	printf("%d\n", *(int *)n->content);
// 	free(n);
// 	return (0);
// }
