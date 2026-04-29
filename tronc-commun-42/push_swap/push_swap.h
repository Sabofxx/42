/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_swap.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PUSH_SWAP_H
# define PUSH_SWAP_H

# include <limits.h>
# include <stddef.h>
# include <stdlib.h>
# include <unistd.h>

typedef struct s_node
{
	int				value;
	int				index;
	struct s_node	*next;
}	t_node;

typedef enum e_strategy
{
	STRAT_SIMPLE,
	STRAT_MEDIUM,
	STRAT_COMPLEX,
	STRAT_ADAPTIVE
}	t_strategy;

typedef enum e_op
{
	OP_SA,
	OP_SB,
	OP_SS,
	OP_PA,
	OP_PB,
	OP_RA,
	OP_RB,
	OP_RR,
	OP_RRA,
	OP_RRB,
	OP_RRR
}	t_op;

typedef struct s_ctx
{
	t_strategy	forced;
	t_strategy	used;
	int			bench;
	double		disorder;
	long		total;
	long		ops[11];
}	t_ctx;

int		parse_input(int argc, char **argv, t_node **a, t_ctx *ctx);
void	error_exit(t_node **a, t_node **b, char **split);
void	free_stack(t_node **stack);
void	free_split(char **split);

size_t	ft_strlen(const char *s);
int		ft_isdigit(int c);
long	ft_atol(const char *str, int *ok);
int		ft_strcmp(const char *s1, const char *s2);
char	*ft_strdup(const char *s);
char	**ft_split_spaces(const char *s);
void	ft_putstr_fd(const char *s, int fd);
void	ft_putnbr_fd(long n, int fd);

void	stack_add_back(t_node **stack, t_node *new_node);
t_node	*stack_new(int value);
int		stack_size(t_node *stack);
int		is_sorted(t_node *stack);
int		find_min_pos(t_node *a);
int		find_max_pos(t_node *b);
void	assign_indexes(t_node *a);

void	log_op(t_ctx *ctx, t_op op, const char *name);
void	op_sa(t_node **a, t_ctx *ctx);
void	op_sb(t_node **b, t_ctx *ctx);
void	op_ss(t_node **a, t_node **b, t_ctx *ctx);
void	op_pa(t_node **a, t_node **b, t_ctx *ctx);
void	op_pb(t_node **a, t_node **b, t_ctx *ctx);
void	op_ra(t_node **a, t_ctx *ctx);
void	op_rb(t_node **b, t_ctx *ctx);
void	op_rr(t_node **a, t_node **b, t_ctx *ctx);
void	op_rra(t_node **a, t_ctx *ctx);
void	op_rrb(t_node **b, t_ctx *ctx);
void	op_rrr(t_node **a, t_node **b, t_ctx *ctx);

void	sort_three(t_node **a, t_ctx *ctx);
void	sort_small_to_five(t_node **a, t_node **b, t_ctx *ctx);
void	simple_sort(t_node **a, t_node **b, t_ctx *ctx);
void	medium_sort(t_node **a, t_node **b, t_ctx *ctx);
void	complex_sort(t_node **a, t_node **b, t_ctx *ctx);
void	run_strategy(t_node **a, t_node **b, t_ctx *ctx);

double	compute_disorder(t_node *a);
void	print_bench(t_ctx *ctx);

#endif
