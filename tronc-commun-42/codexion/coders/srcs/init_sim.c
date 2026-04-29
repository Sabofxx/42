/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   init_sim.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/17 12:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/04/29 17:04:27 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static int	init_one_dongle(t_dongle *d, int id, t_sim *sim)
{
	d->id = id;
	d->in_use = 0;
	d->released_at = 0;
	d->cooldown = sim->cooldown;
	d->inited = 0;
	if (pthread_mutex_init(&d->lock, NULL))
		return (1);
	if (pthread_cond_init(&d->cond, NULL))
	{
		pthread_mutex_destroy(&d->lock);
		return (1);
	}
	if (pq_init(&d->waiters, sim->n, cmp_request))
	{
		pthread_cond_destroy(&d->cond);
		pthread_mutex_destroy(&d->lock);
		return (1);
	}
	d->inited = 1;
	return (0);
}

static int	init_dongles(t_sim *sim)
{
	int	i;

	sim->dongles = malloc(sizeof(t_dongle) * sim->n);
	if (!sim->dongles)
		return (1);
	memset(sim->dongles, 0, sizeof(t_dongle) * sim->n);
	i = -1;
	while (++i < sim->n)
	{
		if (init_one_dongle(&sim->dongles[i], i, sim))
			return (1);
	}
	return (0);
}

static int	init_one_coder(t_coder *c, int id, t_sim *sim)
{
	c->id = id + 1;
	c->compiles_done = 0;
	c->last_compile = 0;
	c->sim = sim;
	c->inited = 0;
	if (pthread_mutex_init(&c->mtx, NULL))
		return (1);
	c->inited = 1;
	return (0);
}

static int	init_coders(t_sim *sim)
{
	int	i;

	sim->coders = malloc(sizeof(t_coder) * sim->n);
	if (!sim->coders)
		return (1);
	memset(sim->coders, 0, sizeof(t_coder) * sim->n);
	i = -1;
	while (++i < sim->n)
	{
		if (init_one_coder(&sim->coders[i], i, sim))
			return (1);
	}
	return (0);
}

int	init_sim(t_sim *sim)
{
	sim->stop = 0;
	sim->dongles = NULL;
	sim->coders = NULL;
	sim->n_threads = 0;
	sim->mon_created = 0;
	if (pthread_mutex_init(&sim->log_mtx, NULL))
		return (1);
	if (init_dongles(sim) || init_coders(sim))
	{
		destroy_sim(sim);
		return (1);
	}
	return (0);
}
