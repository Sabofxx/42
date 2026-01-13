/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strlen.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 12:09:17 by omischle          #+#    #+#             */
/*   Updated: 2026/01/13 16:16:42 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

size_t	ft_strlen(const char *str)
{
    int i;
    i = 0;
    while(str[i])
    {
        i++;
    }
    return (i);
}

// int main()
// {
//     printf("%d\n", ft_strlen("jesaipas"));
// }