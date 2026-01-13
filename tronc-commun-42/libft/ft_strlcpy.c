/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strlcpy.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 14:24:44 by omischle          #+#    #+#             */
/*   Updated: 2026/01/13 14:28:56 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

size_t	ft_strlcpy(char *dst, const char *src, size_t dstsize)
{
    size_t i;

    i = 0;
    if (!dst || !src)
        return (0);
    while(src[i] && i + 1 < dstsize)
    {
        dst[i] = src[i];
        i++;
    }
    if (dstsize > 0)
    {
        dst[i] = '\0';
        i++;

    }
    return (ft_strlen(src));
}