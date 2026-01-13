/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strdup.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 15:26:29 by omischle          #+#    #+#             */
/*   Updated: 2026/01/13 15:31:28 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char    *ft_strdup(const char *s1)
{
    char *new;
    size_t i;

    new = malloc(sizeof(char) * (ft_strlen(s1) + 1));
    if(!new)
        return (NULL);
    i = 0;
    while (s1[i])
    {
        new[i] = s1[i];
        i++;
    }
    new[i] = '\0';
    return (new);
}