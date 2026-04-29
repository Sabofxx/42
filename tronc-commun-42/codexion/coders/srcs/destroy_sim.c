/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   destroy_sim.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/17 12:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/04/29 17:04:10 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static void	destroy_one_dongle(t_dongle *d)
{
	pq_destroy(&d->waiters);
	pthread_cond_destroy(&d->cond);
	pthread_mutex_destroy(&d->lock);
}

void	destroy_sim(t_sim *sim)
{
	int	i;

	if (sim->dongles)
	{
		i = -1;
		while (++i < sim->n)
		{
			if (sim->dongles[i].inited)
				destroy_one_dongle(&sim->dongles[i]);
		}
		free(sim->dongles);
	}
	if (sim->coders)
	{
		i = -1;
		while (++i < sim->n)
		{
			if (sim->coders[i].inited)
				pthread_mutex_destroy(&sim->coders[i].mtx);
		}
		free(sim->coders);
	}
	pthread_mutex_destroy(&sim->log_mtx);
}
