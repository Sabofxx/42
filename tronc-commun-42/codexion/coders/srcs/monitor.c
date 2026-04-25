/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   monitor.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/17 12:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/04/17 12:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static int	check_all_done(t_sim *sim)
{
	int	i;

	i = -1;
	while (++i < sim->n)
	{
		if (get_compiles_done(&sim->coders[i]) < sim->compiles_req)
			return (0);
	}
	return (1);
}

static int	check_burnouts(t_sim *sim)
{
	int		i;
	long	since;

	i = -1;
	while (++i < sim->n)
	{
		since = now_ms() - get_last_compile(&sim->coders[i]);
		if (since >= sim->t_burnout)
			return (sim->coders[i].id);
	}
	return (0);
}

static void	log_burnout(t_sim *sim, int id)
{
	pthread_mutex_lock(&sim->log_mtx);
	if (!sim->stop)
	{
		printf("%ld %d burned out\n",
			now_ms() - sim->start_ms, id);
		sim->stop = 1;
	}
	pthread_mutex_unlock(&sim->log_mtx);
}

void	*monitor_routine(void *arg)
{
	t_sim	*sim;
	int		burned;

	sim = (t_sim *)arg;
	while (1)
	{
		if (check_all_done(sim))
		{
			pthread_mutex_lock(&sim->log_mtx);
			sim->stop = 1;
			pthread_mutex_unlock(&sim->log_mtx);
			return (NULL);
		}
		burned = check_burnouts(sim);
		if (burned > 0)
		{
			log_burnout(sim, burned);
			return (NULL);
		}
		usleep(500);
	}
	return (NULL);
}
