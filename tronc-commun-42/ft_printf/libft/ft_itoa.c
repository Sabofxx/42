/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_itoa.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/14 15:28:20 by omischle          #+#    #+#             */
/*   Updated: 2026/01/14 18:17:26 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static size_t	count_size(long nb)
{
	size_t	size;

	size = 0;
	if (nb < 0)
	{
		nb = nb * (-1);
		size = 1;
	}
	if (nb == 0)
		size = 1;
	else
	{
		while (nb)
		{
			nb = nb / 10;
			size++;
		}
	}
	return (size);
}

char	*ft_itoa(int n)
{
	size_t	size;
	long	nb;
	char	*str;
	int		is_negative;

	size = count_size((long)n);
	str = (char *)malloc(sizeof(char) * (size + 1));
	if (str == NULL)
		return (NULL);
	nb = (long)n;
	is_negative = 0;
	if (nb < 0)
	{
		nb = nb * (-1);
		str[0] = '-';
		is_negative = 1;
	}
	str[size] = '\0';
	while (size > (size_t)is_negative)
	{
		str[size - 1] = nb % 10 + '0';
		nb = nb / 10;
		size--;
	}
	return (str);
}

/* int main(void)
{
	int	numbers[];
    size_t i;
    char *str;

    numbers[] = {0, 123, -456, 2147483647, -2147483648};
    for (i = 0; i < sizeof(numbers) / sizeof(numbers[0]); i++)
    {
        str = ft_itoa(numbers[i]);
        if (str == NULL)
        {
            printf("Erreur d'allocation pour %d\n", numbers[i]);
            continue ;
        }
        printf("ft_itoa(%d) = \"%s\"\n", numbers[i], str);
        free(str); // Toujours libérer la mémoire après usage
    }
    return (0);
}
 */