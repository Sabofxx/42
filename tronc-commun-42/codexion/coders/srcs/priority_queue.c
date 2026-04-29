/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   priority_queue.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/17 12:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/04/29 17:04:40 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

int	pq_init(t_pq *pq, int cap, int (*cmp)(t_request, t_request))
{
	pq->data = malloc(sizeof(t_request) * cap);
	if (!pq->data)
		return (1);
	pq->size = 0;
	pq->cap = cap;
	pq->cmp = cmp;
	return (0);
}

void	pq_push(t_pq *pq, t_request req)
{
	if (pq->size >= pq->cap)
		return ;
	pq->data[pq->size] = req;
	pq->size++;
	sift_up(pq, pq->size - 1);
}

t_request	pq_pop(t_pq *pq)
{
	t_request	top;

	top = pq->data[0];
	pq->size--;
	if (pq->size > 0)
	{
		pq->data[0] = pq->data[pq->size];
		sift_down(pq, 0);
	}
	return (top);
}

t_request	*pq_peek(t_pq *pq)
{
	if (pq->size == 0)
		return (NULL);
	return (&pq->data[0]);
}

void	pq_destroy(t_pq *pq)
{
	if (pq->data)
		free(pq->data);
	pq->data = NULL;
	pq->size = 0;
}
