/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_verif_columns.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/15 13:05:12 by omischle          #+#    #+#             */
/*   Updated: 2025/12/15 13:05:14 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "BSQ.h"

static int	ft_read_line_len(int fd)
{
	ssize_t	read_size;
	int		length;
	char	current;

	read_size = read(fd, &current, 1);
	length = 0;
	while (read_size > 0)
	{
		length++;
		if (current == '\n')
			return (length);
		read_size = read(fd, &current, 1);
	}
	if (read_size < 0)
		return (-1);
	return (length);
}

static int	ft_check_columns_fd(int fd, int line_count, int column_count)
{
	int	index;
	int	line_len;

	index = 0;
	while (index < line_count)
	{
		line_len = ft_read_line_len(fd);
		if (line_len != column_count)
			return (1);
		index++;
	}
	return (0);
}

int	ft_verif_columns(char *argv)
{
	int	fd;
	int	line_count;
	int	column_count;

	column_count = ft_get_number_columns(argv);
	line_count = ft_get_number_lines(argv);
	if (column_count <= 0 || line_count <= 0)
		return (1);
	fd = open(argv, O_RDONLY);
	if (fd < 0)
		return (1);
	ft_get_second_line(fd);
	if (ft_check_columns_fd(fd, line_count, column_count) == 1)
	{
		close(fd);
		return (1);
	}
	close(fd);
	return (0);
}
