/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   dongle_acquire.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/17 12:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/04/17 12:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static t_request	make_request(t_coder *c)
{
	t_request	req;

	req.coder_id = c->id;
	if (c->sim->scheduler == SCH_FIFO)
		req.key = now_ms();
	else
		req.key = get_last_compile(c) + c->sim->t_burnout;
	return (req);
}

static int	can_take(t_dongle *d, int coder_id)
{
	t_request	*top;

	if (d->in_use)
		return (0);
	top = pq_peek(&d->waiters);
	if (!top || top->coder_id != coder_id)
		return (0);
	if (now_ms() < d->released_at + d->cooldown)
		return (0);
	return (1);
}

static void	timed_wait(t_dongle *d)
{
	struct timespec	ts;
	struct timeval	tv;

	gettimeofday(&tv, NULL);
	ts.tv_sec = tv.tv_sec;
	ts.tv_nsec = (tv.tv_usec + 10000) * 1000;
	if (ts.tv_nsec >= 1000000000L)
	{
		ts.tv_sec += ts.tv_nsec / 1000000000L;
		ts.tv_nsec %= 1000000000L;
	}
	pthread_cond_timedwait(&d->cond, &d->lock, &ts);
}

int	acquire_dongle(t_dongle *d, t_coder *c)
{
	t_request	req;

	req = make_request(c);
	pthread_mutex_lock(&d->lock);
	pq_push(&d->waiters, req);
	while (!can_take(d, c->id))
	{
		if (sim_stopped(c->sim))
		{
			pq_remove(&d->waiters, c->id);
			pthread_mutex_unlock(&d->lock);
			return (1);
		}
		timed_wait(d);
	}
	pq_pop(&d->waiters);
	d->in_use = 1;
	pthread_mutex_unlock(&d->lock);
	return (0);
}

void	release_dongle(t_dongle *d)
{
	pthread_mutex_lock(&d->lock);
	d->in_use = 0;
	d->released_at = now_ms();
	pthread_cond_broadcast(&d->cond);
	pthread_mutex_unlock(&d->lock);
}
