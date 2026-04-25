/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/12 15:45:31 by omischle           #+#    #+#             */
/*   Updated: 2026/02/12 16:00:03 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef FT_PRINTF_H
# define FT_PRINTF_H

# include <stdarg.h>
# include <unistd.h>
# include <stdint.h>

int	ft_printf(const char *format, ...);

int	ft_handle(char spec, va_list args);

int	ft_print_char(int c);
int	ft_print_str(char *s);
int	ft_print_percent(void);

int	ft_print_nbr(int n);
int	ft_print_unsigned(unsigned int n);

int	ft_print_hex(unsigned long n, int uppercase);
int	ft_print_ptr(void *ptr);

#endif