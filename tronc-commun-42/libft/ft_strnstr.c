/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   strnstr.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 14:57:03 by omischle          #+#    #+#             */
/*   Updated: 2026/01/13 15:02:50 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strnstr(const char *haystack, const char *needle, size_t len)
{
    size_t len_n;
    size_t i;
    size_t j;
    
    if (!haystack || !needle)
        return (NULL);
    if (ft_strlen(needle) == 0)
        return ((char *) haystack);
    len_n = ft_strlen(needle);
    i = 0;
    while (haystack[i] && i < len)
    {
        j = 0;
        while(haystack[i + j] && haystack[i + j] == needle[j] && i + j < len)
            j++;
        if (j == len_n)
            return ((char *) haystack + i);
        i++;
    }
    return (NULL);
}