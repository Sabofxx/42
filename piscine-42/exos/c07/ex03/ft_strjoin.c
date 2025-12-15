/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strjoin.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/14 15:20:41 by omischle          #+#    #+#             */
/*   Updated: 2025/12/14 15:20:44 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>
#include <stdlib.h>

int	ft_strlen(char *str)
{
	int	i;

	i = 0;
	while (str[i] != '\0')
		i++;
	return (i);
}

char	*ft_all_lenghts(int size, char **strs, char *sep)
{
	int		i;
	int		sum;
	char	*all_together;

	sum = 0;
	i = 0;
	if (size <= 0)
		sum = 1;
	else
	{
		while (i < size)
		{
			sum += ft_strlen(strs[i]);
			i++;
		}
		sum += ft_strlen(sep) * size - 1;
	}
	all_together = (char *)malloc(sizeof(char) * sum);
	if (all_together == NULL)
		return (0);
	return (all_together);
}

char	*ft_strjoin(int size, char **strs, char *sep)
{
	int		i;
	int		j;
	int		c;
	char	*all_together;

	all_together = ft_all_lenghts(size, strs, sep);
	i = 0;
	c = 0;
	while (size > i)
	{
		j = 0;
		while (strs[i][j])
		{
			all_together[c++] = strs[i][j++];
		}
		j = 0;
		while (sep[j] && i != size - 1)
		{
			all_together[c++] = sep[j++];
		}
		i++;
	}
	all_together[c] = '\0';
	return (all_together);
}
/*
int	main(void)
{
	char *strs[] = {"Hello", "world", "this", "is", "a", "test"};
	int size = 6;
	char *sep = " ";
	int	i = 0;
	char	*all_together = ft_strjoin(size, strs, sep);

	while (i < size)
	{
		printf("String in the index %d: %s\n", i, strs[i]);
		i++;
	}
	printf("New string: %s\n", all_together);
	free(all_together);
} */
