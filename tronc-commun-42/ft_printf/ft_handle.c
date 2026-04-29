/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_handle.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/12 15:44:51 by omischle          #+#    #+#             */
/*   Updated: 2026/04/29 17:09:05 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

int	ft_handle(char spec, va_list args)
{
	if (spec == 'c')
		return (ft_print_char(va_arg(args, int)));
	if (spec == 's')
		return (ft_print_str(va_arg(args, char *)));
	if (spec == 'p')
		return (ft_print_ptr(va_arg(args, void *)));
	if (spec == 'd' || spec == 'i')
		return (ft_print_nbr(va_arg(args, int)));
	if (spec == 'u')
		return (ft_print_unsigned(va_arg(args, unsigned int)));
	if (spec == 'x')
		return (ft_print_hex((unsigned long)va_arg(args, unsigned int), 0));
	if (spec == 'X')
		return (ft_print_hex((unsigned long)va_arg(args, unsigned int), 1));
	if (spec == '%')
		return (ft_print_percent());
	if (ft_print_char('%') < 0)
		return (-1);
	return (ft_print_char(spec));
}
