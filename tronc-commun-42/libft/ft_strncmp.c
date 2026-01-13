/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strncmp.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 14:52:46 by omischle          #+#    #+#             */
/*   Updated: 2026/01/13 16:18:45 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

int		ft_strncmp(const char *s1, const char *s2, size_t n)
{
    size_t i;

    i = 0;
    while (s1[i] && s1[i] == s2[i] && i < n)
        i++;
    if ( i < n)
        return ((unsigned char) s1[i] - (unsigned char) s2[i]);
    return (0);
}