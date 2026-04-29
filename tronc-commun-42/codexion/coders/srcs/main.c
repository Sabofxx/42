/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/17 12:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/04/29 17:04:29 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static void	set_start_time(t_sim *sim)
{
	int	i;

	sim->start_ms = now_ms();
	i = -1;
	while (++i < sim->n)
		sim->coders[i].last_compile = sim->start_ms;
}

static int	launch_threads(t_sim *sim)
{
	sim->n_threads = 0;
	sim->mon_created = 0;
	while (sim->n_threads < sim->n)
	{
		if (pthread_create(&sim->coders[sim->n_threads].thread,
				NULL, coder_routine,
				&sim->coders[sim->n_threads]))
		{
			sim->stop = 1;
			return (1);
		}
		sim->n_threads++;
	}
	if (pthread_create(&sim->monitor, NULL, monitor_routine, sim))
	{
		sim->stop = 1;
		return (1);
	}
	sim->mon_created = 1;
	return (0);
}

static void	join_threads(t_sim *sim)
{
	int	i;

	i = -1;
	while (++i < sim->n_threads)
		pthread_join(sim->coders[i].thread, NULL);
	if (sim->mon_created)
		pthread_join(sim->monitor, NULL);
}

int	main(int argc, char **argv)
{
	t_sim	sim;
	int		ret;

	if (argc != 9)
	{
		write(2, "Error: 8 arguments required\n", 28);
		return (1);
	}
	if (parse_args(&sim, argv))
		return (1);
	if (init_sim(&sim))
		return (1);
	set_start_time(&sim);
	ret = launch_threads(&sim);
	join_threads(&sim);
	destroy_sim(&sim);
	return (ret);
}
