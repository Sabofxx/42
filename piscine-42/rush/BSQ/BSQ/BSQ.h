/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   BSQ.h                                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/15 13:06:03 by omischle          #+#    #+#             */
/*   Updated: 2025/12/15 13:06:22 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef BSQ_H
# define BSQ_H
# include <errno.h>
# include <fcntl.h>
# include <stdio.h>
# include <stdlib.h>
# include <sys/types.h>
# include <sys/uio.h>
# include <unistd.h>

typedef struct s_bsq_info
{
	int		columns;
	int		lines;
	char	obstacle;
	char	full;
}	t_bsq_info;

typedef struct s_square
{
	int		size;
	int		position;
}	t_square;

typedef struct s_dp_ctx
{
	char		**map;
	int			**cache;
	t_bsq_info	info;
}	t_dp_ctx;

void	ft_putchar(char c);
void	ft_putstr(char *str);
void	ft_cat(void);
void	ft_putnbr(int nb);
int		ft_get_number_lines(char *argv);
char	ft_get_char_void(char *argv);
char	ft_get_char_obst(char *argv);
char	ft_get_char_full(char *argv);
int		ft_get_number_columns(char *argv);
char	**ft_read_file(char *argv);
void	ft_get_second_line(int fd);
int		ft_strlen(char *str);
char	*ft_strcpy(char *dest, char *src);
int		ft_verif_chars(char *argv);
int		ft_verif_columns(char *argv);
int		ft_verif_returns(char *argv);
int		ft_verif_map(char *argv);
int		ft_atoi(char *str);
void	ft_print_names(int i, int argc, char **argv);
int		ft_size_file(char *argv);
void	ft_display_file(int i, int fd, int argc, char **argv);
int		ft_min(int a, int b, int c);
int		**ft_generate_map(int l, int c);
void	ft_free_int_matrix(int **map, int rows);
int		ft_biggest_square(char **map, t_bsq_info info);
int		ft_find_position_square(char **map, t_bsq_info info);
char	**ft_fill_map(char **map, t_bsq_info info);
void	ft_print_solutions(int i, char *argv);

#endif
