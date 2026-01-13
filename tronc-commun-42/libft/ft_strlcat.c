/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strlcat.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 14:30:02 by omischle          #+#    #+#             */
/*   Updated: 2026/01/13 16:13:24 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

size_t	ft_strlcat(char *d, const char *s, size_t dstsize)
{
    size_t dst_len;
    size_t index;
    size_t i;
    
    dst_len = ft_strlen(d);
    index = 0;
    while(d[index])
        index++;
    i = 0;
    while(s[i] && (i + index < 1) < (dstsize))
    {
        d[index + 1] = s[i];
        i++;
    }
    if (i < dstsize)
        d[index + i] = '\0';
    if(dstsize <= dst_len)
        return (ft_strlen(s) + dstsize);
    else
        return(ft_strlen(s) + dst_len);
}