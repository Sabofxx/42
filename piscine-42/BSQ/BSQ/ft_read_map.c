/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_read_map.c                                      :+:      :+:    :+:   */
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
	while ((ret = read(fd, &buf, 1)) > 0)
		size++;
	close(fd);
	if (ret < 0)
		return (-1);
	return (size);
}

int	ft_get_number_lines(char *argv)
{
	int		nb_l;
	int		fd;
	char	c;
	ssize_t	ret;

	nb_l = 0;
	fd = open(argv, O_RDONLY);
	if (fd < 0)
		return (-1);
	while ((ret = read(fd, &c, 1)) > 0)
	{
		if (c < '0' || c > '9')
			break ;
		nb_l = nb_l * 10 + (c - '0');
	}
	close(fd);
	if (ret < 0)
		return (-1);
	return (nb_l);
}

int	ft_get_number_columns(char *argv)
{
	int		fd;
	int		count;
	char	c;
	ssize_t	ret;

	count = 0;
	fd = open(argv, O_RDONLY);
	if (fd < 0)
		return (-1);
	ft_get_second_line(fd);
	while ((ret = read(fd, &c, 1)) > 0)
	{
		count++;
		if (c == '\n')
		{
			close(fd);
			return (count);
		}
	}
	close(fd);
	return (-1);
}

void	ft_get_second_line(int fd)
{
	char	c;

	while (read(fd, &c, 1) > 0)
	{
		if (c == '\n')
			break ;
	}
}

static void	ft_free_rows(char **buf, int rows)
{
	int	k;

	if (buf == NULL)
		return ;
	k = 0;
	while (k < rows)
	{
		free(buf[k]);
		k++;
	}
}

char	**ft_read_file(char *argv)
{
	char	**buf;
	int		i;
	int		fd;
	int		c;
	int		ret;
	int		l;

	i = 0;
	ret = 0;
	c = ft_get_number_columns(argv);
	l = ft_get_number_lines(argv);
	if (c <= 0 || l <= 0)
		return (NULL);
	fd = open(argv, O_RDONLY);
	if (fd < 0)
		return (NULL);
	ft_get_second_line(fd);
	if ((buf = malloc(l * sizeof(char *))) == NULL)
	{
		close(fd);
		return (NULL);
	}
	while (i < l)
	{
		if ((buf[i] = malloc(c * sizeof(char))) == NULL)
		{
			ft_free_rows(buf, i);
			free(buf);
			close(fd);
			return (NULL);
		}
		i++;
	}
	i = 0;
	while (i < l)
	{
		ret = read(fd, buf[i], c);
		if (ret != c)
		{
			ft_free_rows(buf, l);
			free(buf);
			close(fd);
			return (NULL);
		}
		buf[i][c - 1] = '\0';
		i++;
	}
	close(fd);
	return (buf);
}
