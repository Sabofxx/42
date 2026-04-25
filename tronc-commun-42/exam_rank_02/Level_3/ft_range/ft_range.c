/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_range.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: columbux <columbux@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/05/30 18:23:46 by ahiguera          #+#    #+#             */
/*   Updated: 2024/05/30 19:43:30 by columbux         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

/* #include <stdio.h>
#include <stdlib.h> */

int     *ft_range(int start, int end)
{
	int	*result;
	int		i;
	int		len;

	i = 0;
	len = abs(start - end + 1);
	result = (int *)malloc(len);
	while (i < len)
	{
		if (start <= end)
			result[i++] = start++;
		else if (start >= end)
			result[i++] = start--;
	}
	return(result);
}
/* 
int	main(int argc, char **argv)
{
	if (argc == 3)
		printf("%ls", ft_range(atoi(argv[1]), atoi(argv[2])));
	printf("\n");
	return(0);
}
 */