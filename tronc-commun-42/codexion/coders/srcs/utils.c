/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   utils.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/17 12:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/04/17 12:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

long	now_ms(void)
{
	struct timeval	tv;

	gettimeofday(&tv, NULL);
	return (tv.tv_sec * 1000L + tv.tv_usec / 1000);
}

void	precise_sleep(long ms, t_sim *sim)
{
	long	start;

	start = now_ms();
	while (now_ms() - start < ms)
	{
		if (sim_stopped(sim))
			return ;
		usleep(200);
	}
}

void	log_state(t_coder *c, const char *msg)
{
	pthread_mutex_lock(&c->sim->log_mtx);
	if (!c->sim->stop)
		printf("%ld %d %s\n", now_ms() - c->sim->start_ms, c->id, msg);
	pthread_mutex_unlock(&c->sim->log_mtx);
}

int	sim_stopped(t_sim *sim)
{
	int	val;

	pthread_mutex_lock(&sim->log_mtx);
	val = sim->stop;
	pthread_mutex_unlock(&sim->log_mtx);
	return (val);
}
