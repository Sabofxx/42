/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strchr.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 14:35:05 by omischle          #+#    #+#             */
/*   Updated: 2026/01/13 14:51:51 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strrchr(const char *s, int c)
{
    int i;

    if (!s)
        return NULL;
    i = ft_strlen(s);
    while( i >= 0)
    {
        if (s[i] == (char) c)
            return ((char *) s + 1);
        i--;
    }
    return (NULL);
}