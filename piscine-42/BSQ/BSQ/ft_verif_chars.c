/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_verif_chars.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/15 13:04:56 by omischle          #+#    #+#             */
/*   Updated: 2025/12/15 13:04:57 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "BSQ.h"

static int	ft_chunk_has_invalid(char *buffer, ssize_t size, char char_void,
		char char_obst)
{
	int	index;

	index = 0;
	while (index < size)
	{
		if (buffer[index] != char_void && buffer[index] != char_obst
			&& buffer[index] != '\n')
			return (1);
		index++;
	}
	return (0);
}

static int	ft_check_chars_fd(int fd, int file_size, char char_void,
		char char_obst)
{
	char	*buffer;
	ssize_t	read_size;

	buffer = malloc(file_size * sizeof(char));
	if (buffer == NULL)
		return (1);
	read_size = read(fd, buffer, file_size);
	while (read_size > 0)
	{
		if (ft_chunk_has_invalid(buffer, read_size, char_void, char_obst) == 1)
		{
			free(buffer);
			return (1);
		}
		read_size = read(fd, buffer, file_size);
	}
	free(buffer);
	if (read_size < 0)
		return (1);
	return (0);
}

int	ft_verif_chars(char *argv)
{
	int		fd;
	int		file_size;
	char	char_void;
	char	char_obst;

	char_void = ft_get_char_void(argv);
	char_obst = ft_get_char_obst(argv);
	file_size = ft_size_file(argv);
	if (file_size <= 0)
		return (1);
	fd = open(argv, O_RDONLY);
	if (fd < 0)
		return (1);
	ft_get_second_line(fd);
	if (ft_check_chars_fd(fd, file_size, char_void, char_obst) == 1)
	{
		close(fd);
		return (1);
	}
	close(fd);
	return (0);
}
