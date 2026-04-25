/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_putchar_fd.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/15 16:08:20 by omischle           #+#    #+#             */
/*   Updated: 2026/01/15 16:09:39 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	ft_putchar_fd(char c, int fd)
{
	write(fd, &c, 1);
}
// #include <fcntl.h>
// int	main(void)
// {
// 	ft_putchar_fd('A', 1);
// 	ft_putchar_fd('\n', 1);
// 	ft_putchar_fd('Z', 1);
// 	ft_putchar_fd('\n', 1);
// 	return (0);
// }