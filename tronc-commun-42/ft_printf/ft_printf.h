/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/30 15:06:06 by omischle          #+#    #+#             */
/*   Updated: 2026/01/30 15:19:01 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef FT_PRINTF_H
# define FT_PRINTF_H
# include <stdarg.h>
# include <limits.h>
# include <stdint.h>
# include <stdlib.h>
# include <unistd.h>
# include <stdio.h>
# include "libft/libft.h"

int	printf_char(int c);
int	printf_string(char *s);
int	printf_ptr(void *ptr);
int	ft_printf(const char *s, ...);
int	printf_nbr(int n);
int	printf_hex(unsigned int n, int x_switch);
int	printf_uint(unsigned int n);

#endif