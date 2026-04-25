/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parse_args.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/17 12:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/04/17 12:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static int	parse_one(char *str, long *out)
{
	long	val;
	int		i;

	val = 0;
	i = 0;
	if (!str[0])
		return (1);
	while (str[i])
	{
		if (str[i] < '0' || str[i] > '9')
			return (1);
		val = val * 10 + (str[i] - '0');
		i++;
	}
	*out = val;
	return (0);
}

static int	parse_numbers(t_sim *sim, char **av)
{
	long	tmp;

	if (parse_one(av[1], &tmp) || tmp < 1)
		return (1);
	sim->n = (int)tmp;
	if (parse_one(av[2], &sim->t_burnout))
		return (1);
	if (parse_one(av[3], &sim->t_compile))
		return (1);
	if (parse_one(av[4], &sim->t_debug))
		return (1);
	if (parse_one(av[5], &sim->t_refactor))
		return (1);
	if (parse_one(av[6], &tmp))
		return (1);
	sim->compiles_req = (int)tmp;
	if (parse_one(av[7], &sim->cooldown))
		return (1);
	return (0);
}

static int	parse_sched(char *str, t_sched *out)
{
	if (strcmp(str, "fifo") == 0)
		*out = SCH_FIFO;
	else if (strcmp(str, "edf") == 0)
		*out = SCH_EDF;
	else
		return (1);
	return (0);
}

int	parse_args(t_sim *sim, char **av)
{
	if (parse_numbers(sim, av))
	{
		write(2, "Error: invalid arguments\n", 25);
		return (1);
	}
	if (parse_sched(av[8], &sim->scheduler))
	{
		write(2, "Error: scheduler must be fifo or edf\n", 37);
		return (1);
	}
	return (0);
}
