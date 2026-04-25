/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_print_ptr.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/12 15:45:08 by omischle           #+#    #+#             */
/*   Updated: 2026/03/02 09:50:05 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

int	ft_print_ptr(void *ptr)
{
	unsigned long	addr;
	int				count;
	int				ret;

	if (!ptr)
		return (ft_print_str("(nil)"));
	addr = (unsigned long)(uintptr_t)ptr;
	count = 0;
	ret = (int)write(1, "0x", 2);
	if (ret < 0)
		return (-1);
	count += ret;
	ret = ft_print_hex(addr, 0);
	if (ret < 0)
		return (-1);
	count += ret;
	return (count);
}
