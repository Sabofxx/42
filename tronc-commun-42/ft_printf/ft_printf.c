/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/12 14:37:43 by omischle           #+#    #+#             */
/*   Updated: 2026/02/12 15:46:55 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

static int	ft_add(int *count, int ret)
{
	if (ret < 0)
		return (-1);
	*count += ret;
	return (0);
}

static int	ft_process(const char *format, va_list args, int *count)
{
	int	i;
	int	ret;

	i = 0;
	while (format[i])
	{
		if (format[i] == '%')
		{
			i++;
			if (!format[i])
				break ;
			ret = ft_handle(format[i], args);
		}
		else
			ret = (int)write(1, &format[i], 1);
		if (ft_add(count, ret) < 0)
			return (-1);
		i++;
	}
	return (0);
}

int	ft_printf(const char *format, ...)
{
	va_list	args;
	int		count;

	if (!format)
		return (-1);
	count = 0;
	va_start(args, format);
	if (ft_process(format, args, &count) < 0)
	{
		va_end(args);
		return (-1);
	}
	va_end(args);
	return (count);
}
