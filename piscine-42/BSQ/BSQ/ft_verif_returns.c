#include "BSQ.h"

static int	ft_close_fail(int fd, char *buffer)
{
	if (buffer != NULL)
		free(buffer);
	close(fd);
	return (1);
}

static int	ft_scan_returns(int fd, char *buffer, int column_count)
{
	ssize_t	read_size;

	read_size = read(fd, buffer, column_count);
	while (read_size > 0)
	{
		if (read_size != column_count || buffer[read_size - 1] != '\n')
			return (1);
		read_size = read(fd, buffer, column_count);
	}
	if (read_size < 0)
		return (1);
	return (0);
}

int	ft_verif_returns(char *argv)
{
	int		fd;
	int		column_count;
	char	*buffer;

	column_count = ft_get_number_columns(argv);
	if (column_count <= 0)
		return (1);
	fd = open(argv, O_RDONLY);
	if (fd < 0)
		return (1);
	ft_get_second_line(fd);
	buffer = malloc(column_count * sizeof(char));
	if (buffer == NULL)
		return (ft_close_fail(fd, NULL));
	if (ft_scan_returns(fd, buffer, column_count) == 1)
		return (ft_close_fail(fd, buffer));
	free(buffer);
	close(fd);
	return (0);
}
