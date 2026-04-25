/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   coder.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/17 12:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/04/17 12:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

void	update_last_compile(t_coder *c)
{
	pthread_mutex_lock(&c->mtx);
	c->last_compile = now_ms();
	pthread_mutex_unlock(&c->mtx);
}

long	get_last_compile(t_coder *c)
{
	long	val;

	pthread_mutex_lock(&c->mtx);
	val = c->last_compile;
	pthread_mutex_unlock(&c->mtx);
	return (val);
}

int	get_compiles_done(t_coder *c)
{
	int	val;

	pthread_mutex_lock(&c->mtx);
	val = c->compiles_done;
	pthread_mutex_unlock(&c->mtx);
	return (val);
}

void	inc_compiles_done(t_coder *c)
{
	pthread_mutex_lock(&c->mtx);
	c->compiles_done++;
	pthread_mutex_unlock(&c->mtx);
}

void	*coder_routine(void *arg)
{
	t_coder	*c;

	c = (t_coder *)arg;
	while (!sim_stopped(c->sim))
	{
		if (take_dongles(c))
			break ;
		update_last_compile(c);
		log_state(c, "is compiling");
		precise_sleep(c->sim->t_compile, c->sim);
		release_dongles(c);
		inc_compiles_done(c);
		if (sim_stopped(c->sim))
			break ;
		log_state(c, "is debugging");
		precise_sleep(c->sim->t_debug, c->sim);
		if (sim_stopped(c->sim))
			break ;
		log_state(c, "is refactoring");
		precise_sleep(c->sim->t_refactor, c->sim);
	}
	return (NULL);
}
