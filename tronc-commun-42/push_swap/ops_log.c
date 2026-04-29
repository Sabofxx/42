/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ops_log.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/03/10 14:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/03/10 14:00:00 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	log_op(t_ctx *ctx, t_op op, const char *name)
{
	if (!ctx)
		return ;
	ctx->ops[op]++;
	ctx->total++;
	write(1, name, ft_strlen(name));
}
