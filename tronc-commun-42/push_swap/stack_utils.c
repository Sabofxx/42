/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stack_utils.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle             #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static void	sort_array(int *arr, int size)
{
	int	i;
	int	j;
	int	tmp;

	i = 0;
	while (i < size - 1)
	{
		j = 0;
		while (j < size - i - 1)
		{
			if (arr[j] > arr[j + 1])
			{
				tmp = arr[j];
				arr[j] = arr[j + 1];
				arr[j + 1] = tmp;
			}
			j++;
		}
		i++;
	}
}

static int	find_index(int *arr, int size, int value)
{
	int	i;

	i = 0;
	while (i < size)
	{
		if (arr[i] == value)
			return (i);
		i++;
	}
	return (-1);
}

void	assign_indexes(t_node *a)
{
	int		*arr;
	int		i;
	int		size;
	t_node	*tmp;

	size = stack_size(a);
	arr = (int *)malloc(sizeof(int) * size);
	if (!arr)
		return ;
	tmp = a;
	i = 0;
	while (tmp)
	{
		arr[i++] = tmp->value;
		tmp = tmp->next;
	}
	sort_array(arr, size);
	while (a)
	{
		a->index = find_index(arr, size, a->value);
		a = a->next;
	}
	free(arr);
}

int	find_min_pos(t_node *a)
{
	int	pos;
	int	min_pos;
	int	min_val;

	pos = 0;
	min_pos = 0;
	min_val = a->value;
	while (a)
	{
		if (a->value < min_val)
		{
			min_val = a->value;
			min_pos = pos;
		}
		a = a->next;
		pos++;
	}
	return (min_pos);
}

int	find_max_pos(t_node *b)
{
	int	pos;
	int	max_pos;
	int	max_val;

	pos = 0;
	max_pos = 0;
	max_val = b->index;
	while (b)
	{
		if (b->index > max_val)
		{
			max_val = b->index;
			max_pos = pos;
		}
		b = b->next;
		pos++;
	}
	return (max_pos);
}
