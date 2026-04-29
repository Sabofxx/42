/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_isalpha.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 11:47:06 by omischle          #+#    #+#             */
/*   Updated: 2026/01/13 14:33:14 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

int	ft_isalpha(int c)
{
	if ((c >= 'A' && c <= 'Z')
		|| (c >= 'a' && c <= 'z'))
		return (1);
	return (0);
}
// #include <stdio.h>
// int	main(void)
// {
// 	printf("%d\n", ft_isalpha('a'));
// 	printf("%d\n", ft_isalpha('5'));
// 	printf("%d\n", ft_isalpha('?'));
// 	return (0);
// }