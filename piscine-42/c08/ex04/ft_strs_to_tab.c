/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strs_to_tab.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: colassin <colassin@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/11 17:27:02 by colassin          #+#    #+#             */
/*   Updated: 2025/12/12 10:30:05 by colassin         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_stock_str.h"
#include <stdio.h>
#include <stdlib.h>

int	ft_strlen(char *str)
{
	int	len;

	len = 0;
	while (str[len])
		len++;
	return (len);
}

char	*ft_strdup(char *src)
{
	char	*str;
	int		src_len;
	int		i;

	i = 0;
	src_len = ft_strlen(src);
	str = malloc(sizeof(char) * src_len + 1);
	if (str == NULL)
	{
		return (0);
	}
	while (src[i])
	{
		str[i] = src[i];
		i++;
	}
	str[i] = '\0';
	return (str);
}

struct s_stock_str	*ft_strs_to_tab(int ac, char **av)
{
	t_stock_str	*tab;
	int			i;

	tab = malloc(sizeof(t_stock_str) * (ac + 1));
	if (!tab)
		return (NULL);
	i = 0;
	while (i < ac)
	{
		tab[i].str = av[i];
		tab[i].size = ft_strlen(av[i]);
		tab[i].copy = ft_strdup(av[i]);
		i++;
	}
	tab[i].str = 0;
	return (tab);
}
/*
int	main(void)
{
	char *strings[] = {"Hello", "World", "42", "Test"};
	t_stock_str *result;
	int i;

	result = ft_strs_to_tab(4, strings);

	if (!result)
	{
		printf("Error: malloc failed\n");
		return (1);
	}

	i = 0;
	while (result[i].str != NULL)
	{
		printf("--- Element %d ---\n", i);
		printf("size: %d\n", result[i].size);
		printf("str:  %s\n", result[i].str);
		printf("copy: %s\n\n", result[i].copy);
		i++;
	}

	return (0);
} */