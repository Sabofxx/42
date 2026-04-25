/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_calloc.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/14 16:12:27 by omischle           #+#    #+#             */
/*   Updated: 2026/01/19 18:59:20 by omischle            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"
#include <stdint.h>

void	*ft_calloc(size_t count, size_t size)
{
	void	*ptr;
	size_t	total;

	if (size != 0 && count > SIZE_MAX / size)
		return (NULL);
	total = count * size;
	ptr = malloc(total);
	if (!ptr)
		return (NULL);
	ft_bzero(ptr, total);
	return (ptr);
}
// #include <stdlib.h>
// #include "libft.h"
// int	main(void)
// {
// 	int	*i;
// 	int	j;
// 	i = (int *)ft_calloc(5, sizeof(int));
// 	if (!i)
// 		return (1);
// 	j = 0;
// 	while (j < 5)
// 	{
// 		printf("%d ", i[j]);
// 		j++;
// 	}
// 	printf("\n");
// 	free(i);
// 	return (0);
// }