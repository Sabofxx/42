/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   pq_helpers.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/17 12:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/04/17 12:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static void	pq_swap(t_pq *pq, int a, int b)
{
	t_request	tmp;

	tmp = pq->data[a];
	pq->data[a] = pq->data[b];
	pq->data[b] = tmp;
}

void	sift_up(t_pq *pq, int i)
{
	int	parent;

	while (i > 0)
	{
		parent = (i - 1) / 2;
		if (!pq->cmp(pq->data[parent], pq->data[i]))
			break ;
		pq_swap(pq, i, parent);
		i = parent;
	}
}

void	sift_down(t_pq *pq, int i)
{
	int	min;
	int	l;
	int	r;

	while (1)
	{
		min = i;
		l = 2 * i + 1;
		r = 2 * i + 2;
		if (l < pq->size
			&& pq->cmp(pq->data[min], pq->data[l]))
			min = l;
		if (r < pq->size
			&& pq->cmp(pq->data[min], pq->data[r]))
			min = r;
		if (min == i)
			break ;
		pq_swap(pq, i, min);
		i = min;
	}
}

int	cmp_request(t_request a, t_request b)
{
	if (a.key == b.key)
		return (a.coder_id > b.coder_id);
	return (a.key > b.key);
}

void	pq_remove(t_pq *pq, int coder_id)
{
	int	i;

	i = 0;
	while (i < pq->size)
	{
		if (pq->data[i].coder_id == coder_id)
		{
			pq->data[i] = pq->data[pq->size - 1];
			pq->size--;
			if (i < pq->size)
			{
				sift_down(pq, i);
				sift_up(pq, i);
			}
			return ;
		}
		i++;
	}
}
