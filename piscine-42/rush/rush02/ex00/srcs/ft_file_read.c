/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_file_read.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: ppeuvrel <ppeuvrel@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/14 12:04:56 by ppeuvrel          #+#    #+#             */
/*   Updated: 2025/12/14 18:02:43 by ppeuvrel         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_h.h"

char	*addchar(char *str, char *buf)
{
	int		i;
	char	*new;

	i = 0;
	while (str[i])
		i++;
	new = malloc(sizeof(char) * (i + 2));
	if (new == NULL)
		return (NULL);
	i = -1;
	while (str[++i])
		new[i] = str[i];
	new[i] = buf[0];
	new[i + 1] = '\0';
	free(str);
	return (new);
}

int	handle_newline(char **str, t_dict **begin)
{
	if (parse_dict(begin, *str))
	{
		free(*str);
		*str = malloc(sizeof(char));
		if (!*str)
			return (0);
		(*str)[0] = '\0';
		return (1);
	}
	if (ft_strlen(*str) != 0)
		return (0);
	return (1);
}

int	gest_buf(int file, t_dict **begin)
{
	int		size;
	char	*str;
	char	buf[1];

	str = malloc(sizeof(char));
	if (!str)
		return (0);
	str[0] = '\0';
	size = read(file, buf, 1);
	while (size != 0)
	{
		if (buf[0] != '\n')
		{
			str = addchar(str, buf);
			if (!str)
				return (0);
		}
		else if (!handle_newline(&str, begin))
			return (0);
		size = read(file, buf, 1);
	}
	ft_list_sort(begin);
	free(str);
	return (1);
}

int	ft_file_read(char *filepath, t_dict **begin)
{
	int	file;

	file = open(filepath, O_RDWR);
	if (file == -1)
		return (0);
	if (!gest_buf(file, begin))
		return (-1);
	return (1);
}
