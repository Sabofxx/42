#include "BSQ.h"

int         ft_verif_chars(char *argv)
{
    int fd;
    int size_file;
    ssize_t ret;
    char *buf;
    char v;
    char o;

    v = ft_get_char_void(argv);
    o = ft_get_char_obst(argv);
    size_file = ft_size_file(argv);
    if (size_file <= 0)
        return (1);
    fd = open(argv, O_RDONLY);
    if (fd < 0)
        return (1);
    ft_get_second_line(fd);
    if ((buf = malloc(size_file * sizeof(char))) == NULL)
    {
        close(fd);
        return (1);
    }
    while ((ret = read(fd, buf, size_file)) > 0)
    {
        int i;

        i = 0;
        while (i < ret)
        {
            if (buf[i] != v && buf[i] != o && buf[i] != '\n')
            {
                free(buf);
                close(fd);
                return (1);
            }
            i++;
        }
    }
    free(buf);
    close(fd);
    return (ret < 0);
}

int             ft_get_next_columns(int fd)
{
    char c;
    ssize_t ret;
    int count;

    count = 0;
    while ((ret = read(fd, &c, 1)) > 0)
    {
        count++;
        if (c == '\n')
            return (count);
    }
    if (ret < 0)
        return (-1);
    return (count);
}

int         ft_verif_columns(char *argv)
{
    int i;
    int fd;
    int j;
    int c;
    int l;

    i = 0;
    c = ft_get_number_columns(argv);
    l = ft_get_number_lines(argv);
    if (c <= 0 || l <= 0)
        return (1);
    fd = open(argv, O_RDONLY);
    if (fd < 0)
        return (1);
    ft_get_second_line(fd);
    while (i < l)
    {
        j = ft_get_next_columns(fd);
        if (j != c)
        {
            close(fd);
            return (1);
        }
        i++;
    }
    close(fd);
    return (0);
}

int         ft_verif_returns(char *argv)
{
    char *buf;
    int fd;
    ssize_t ret;
    int c;

    c = ft_get_number_columns(argv);
    if (c <= 0)
        return (1);
    fd = open(argv, O_RDONLY);
    if (fd < 0)
        return (1);
    ft_get_second_line(fd);
    if ((buf = malloc(c * sizeof(char))) == NULL)
    {
        close(fd);
        return (1);
    }
    while ((ret = read(fd, buf, c)) > 0)
    {
        if (ret != c || buf[ret - 1] != '\n')
        {
            free(buf);
            close(fd);
            return (1);
        }
    }
    free(buf);
    close(fd);
    return (ret < 0);
}
int        ft_verif_map(char *argv)
{
    if (ft_get_number_columns(argv) < 1 || ft_get_number_lines(argv) < 1)
    {
            ft_putstr("map error\n");
            return (1);
    }
    if (ft_verif_chars(argv) == 1 || ft_verif_returns(argv) == 1)
    {
            ft_putstr("map error\n");
            return (1);
    }
    if (ft_verif_columns(argv) == 1)
    {
            ft_putstr("map error\n");
            return (1);
    }
    return (0);
}
