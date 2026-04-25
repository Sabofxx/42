/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_isascii.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 11:47:11 by omischle           #+#    #+#             */
/*   Updated: 2026/01/13 14:35:29 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

int	ft_isascii(int c)
{
	if (c >= 0 && c <= 127)
		return (1);
	return (0);
}
// #include <stdio.h>

// int	main(void)
// {
// 	printf("%d\n", ft_isascii('A'));      
// 	printf("%d\n", ft_isascii(127));     
// 	printf("%d\n", ft_isascii(-1));    
// 	return (0);
// }
