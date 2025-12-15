/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_map_info.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/15 13:04:11 by omischle          #+#    #+#             */
/*   Updated: 2025/12/15 13:04:12 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "BSQ.h"

int	ft_size_file(char *argv)
{
	int		size;
	char	buf;
	int		fd;
	ssize_t	ret;

	size = 0;
	fd = open(argv, O_RDONLY);
	if (fd < 0)
		return (-1);
	ret = read(fd, &buf, 1);
	while (ret > 0)
	{
		size++;
		ret = read(fd, &buf, 1);
	}
	close(fd);
	if (ret < 0)
		return (-1);
	return (size);
}

void	ft_get_second_line(int fd)
{
	char	c;
	ssize_t	ret;

	ret = read(fd, &c, 1);
	while (ret > 0)
	{
		if (c == '\n')
			return ;
		ret = read(fd, &c, 1);
	}
}

int	ft_get_number_lines(char *argv)
{
	int		nb_lines;
	int		fd;
	char	c;
	ssize_t	ret;

	nb_lines = 0;
	fd = open(argv, O_RDONLY);
	if (fd < 0)
		return (-1);
	ret = read(fd, &c, 1);
	while (ret > 0)
	{
		if (c < '0' || c > '9')
			break ;
		nb_lines = nb_lines * 10 + (c - '0');
		ret = read(fd, &c, 1);
	}
	close(fd);
	if (ret < 0)
		return (-1);
	return (nb_lines);
}

int	ft_get_number_columns(char *argv)
{
	int		count;
	int		fd;
	char	c;
	ssize_t	ret;

	count = 0;
	fd = open(argv, O_RDONLY);
	if (fd < 0)
		return (-1);
	ft_get_second_line(fd);
	ret = read(fd, &c, 1);
	while (ret > 0)
	{
		count++;
		if (c == '\n')
		{
			close(fd);
			return (count);
		}
		ret = read(fd, &c, 1);
	}
	close(fd);
	return (-1);
}
