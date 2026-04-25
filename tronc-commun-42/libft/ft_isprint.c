/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_isprint.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 11:47:36 by omischle           #+#    #+#             */
/*   Updated: 2026/01/13 16:26:49 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

int	ft_isprint(int c)
{
	if (c >= 32 && c <= 126)
		return (1);
	return (0);
}
// #include <stdio.h>
// int	main(void)
// {
// 	printf("%d\n", ft_isprint('A'));  
// 	printf("%d\n", ft_isprint(' '));   
// 	printf("%d\n", ft_isprint('\n'));  
// 	printf("%d\n", ft_isprint(127));   
// 	return (0);
// }
