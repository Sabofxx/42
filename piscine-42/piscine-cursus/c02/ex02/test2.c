/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   test2.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <marvin@42.fr>                    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 16:27:59 by omischle          #+#    #+#             */
/*   Updated: 2025/12/04 16:40:55 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>

int ft_str_is_alpha(char *str)
{
	int i;
	i = 0;

	while (str[i])
	{
		if (!((str[i] >= 'a') && (str[i] <= 'z')
				       || (str[i] >= 'A') && (str[i] <= 'Z')))
			return 0;
		i++;	
	}
	return 1;
}

int main()
{
	char driss[] = "DriFIHweihf3363";
	char driss1[] = "lksaFSJKBhflowfhlwhf";

	printf("%s is alpha ? reponse : %d\n", driss, ft_str_is_alpha(driss));
	printf("%s is alpha ? reponse : %d\n", driss1, ft_str_is_alpha(driss1));
}
