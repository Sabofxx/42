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

static void	ft_free_rows(char **buf, int rows)
{
	int	index;

	if (buf == NULL)
		return ;
	index = 0;
	while (index < rows)
	{
		free(buf[index]);
		index++;
	}
}

static char	**ft_alloc_rows(int lines, int columns)
{
	char	**buf;
	int		index;

	buf = malloc(lines * sizeof(char *));
	if (buf == NULL)
		return (NULL);
	index = 0;
	while (index < lines)
	{
		buf[index] = malloc(columns * sizeof(char));
		if (buf[index] == NULL)
		{
			ft_free_rows(buf, index);
			free(buf);
			return (NULL);
		}
		index++;
	}
	return (buf);
}

static int	ft_load_rows(int fd, char **buf, int lines, int columns)
{
	int			row;
	ssize_t		ret;

	row = 0;
	while (row < lines)
	{
		ret = read(fd, buf[row], columns);
		if (ret != columns)
			return (0);
		buf[row][columns - 1] = '\0';
		row++;
	}
	return (1);
}

static int	ft_prepare_reader(char *argv, int *fd, int *columns, int *lines)
{
	*columns = ft_get_number_columns(argv);
	*lines = ft_get_number_lines(argv);
	if (*columns <= 0 || *lines <= 0)
		return (0);
	*fd = open(argv, O_RDONLY);
	if (*fd < 0)
		return (0);
	ft_get_second_line(*fd);
	return (1);
}

char	**ft_read_file(char *argv)
{
	char	**buf;
	int		fd;
	int		columns;
	int		lines;

	if (!ft_prepare_reader(argv, &fd, &columns, &lines))
		return (NULL);
	buf = ft_alloc_rows(lines, columns);
	if (buf == NULL)
	{
		close(fd);
		return (NULL);
	}
	if (!ft_load_rows(fd, buf, lines, columns))
	{
		ft_free_rows(buf, lines);
		free(buf);
		close(fd);
		return (NULL);
	}
	close(fd);
	return (buf);
}
