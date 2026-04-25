/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   dongle.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/17 12:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/04/17 12:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static void	get_dongle_ids(t_coder *c, int *first, int *second)
{
	int	left;
	int	right;

	left = c->id - 1;
	right = c->id % c->sim->n;
	if (left <= right)
	{
		*first = left;
		*second = right;
	}
	else
	{
		*first = right;
		*second = left;
	}
}

static int	wait_for_stop(t_coder *c)
{
	while (!sim_stopped(c->sim))
		usleep(1000);
	return (1);
}

int	take_dongles(t_coder *c)
{
	int	first;
	int	second;

	get_dongle_ids(c, &first, &second);
	if (first == second)
		return (wait_for_stop(c));
	if (acquire_dongle(&c->sim->dongles[first], c))
		return (1);
	log_state(c, "has taken a dongle");
	if (acquire_dongle(&c->sim->dongles[second], c))
	{
		release_dongle(&c->sim->dongles[first]);
		return (1);
	}
	log_state(c, "has taken a dongle");
	return (0);
}

void	release_dongles(t_coder *c)
{
	int	first;
	int	second;

	get_dongle_ids(c, &first, &second);
	release_dongle(&c->sim->dongles[first]);
	release_dongle(&c->sim->dongles[second]);
}
