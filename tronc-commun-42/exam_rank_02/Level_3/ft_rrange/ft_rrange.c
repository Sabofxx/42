/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_rrange.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: columbux <columbux@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/05/30 19:40:03 by ahiguera          #+#    #+#             */
/*   Updated: 2024/05/30 19:44:49 by columbux         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

/* #include <stdio.h>
#include <stdlib.h> */

int     *ft_rrange(int start, int end)
{
	int	*result;
	int		i;
	int		len;

	i = 0;
	len = abs(end - start + 1);
	result = (int *)malloc(len);
	while (i < len)
	{
		if (end <= start)
			result[i++] = end++;
		else if (end >= start)
			result[i++] = end--;
	}
	return(result);
}
/* 
int	main(int argc, char **argv)
{
	if (argc == 3)
		{	
		printf("%ls", ft_rrange(atoi(argv[1]), atoi(argv[2])));
		free();
		}
	printf("\n");
	return(0);
}
 */