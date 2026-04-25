/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   get_next_line.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/30 12:06:01 by omischle           #+#    #+#             */
/*   Updated: 2026/01/30 12:06:02 by omischle          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "get_next_line.h"

static char	*gnl_join_free(char *stash, char *buf)
{
	char	*tmp;

	tmp = ft_strjoin(stash, buf);
	free(stash);
	return (tmp);
}

static char	*gnl_read(int fd, char *stash)
{
	char	*buf;
	ssize_t	r;

	buf = (char *)malloc((size_t)BUFFER_SIZE + 1);
	if (!buf)
		return (free(stash), NULL);
	r = 1;
	while (!ft_strchr(stash, '\n') && r > 0)
	{
		r = read(fd, buf, BUFFER_SIZE);
		if (r < 0)
			return (free(buf), free(stash), NULL);
		buf[r] = '\0';
		stash = gnl_join_free(stash, buf);
		if (!stash)
			return (free(buf), NULL);
	}
	return (free(buf), stash);
}

static char	*gnl_line(char *stash)
{
	size_t	i;

	if (!stash || !stash[0])
		return (NULL);
	i = 0;
	while (stash[i] && stash[i] != '\n')
		i++;
	if (stash[i] == '\n')
		return (ft_substr(stash, 0, i + 1));
	return (ft_substr(stash, 0, i));
}

static char	*gnl_next(char *stash)
{
	size_t	i;
	size_t	len;
	char	*next;

	i = 0;
	while (stash[i] && stash[i] != '\n')
		i++;
	if (!stash[i])
		return (free(stash), NULL);
	len = ft_strlen(stash);
	next = ft_substr(stash, i + 1, len - i - 1);
	free(stash);
	if (!next || !next[0])
		return (free(next), NULL);
	return (next);
}

char	*get_next_line(int fd)
{
	static char	*stash;
	char		*line;

	if (fd < 0 || BUFFER_SIZE <= 0)
		return (NULL);
	stash = gnl_read(fd, stash);
	if (!stash)
		return (NULL);
	line = gnl_line(stash);
	stash = gnl_next(stash);
	return (line);
}
