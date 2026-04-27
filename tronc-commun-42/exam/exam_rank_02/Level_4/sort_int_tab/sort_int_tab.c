/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sort_int_tab.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>                  +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/05/24 08:24:39 by omischle              #+#    #+#             */
/*   Updated: 2024/06/24 11:36:06 by omischle             ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

void	swap(int *a, int *b)
{
	int	temp;

	temp = *a;
	*a = *b;
	*b = temp;
}

void	sort_in_tab(int *tab, unsigned int size)
{
	int	i;

	i = 0;
	while (i < (size - 1))
	{
		if (tab[i] > tab[i + 1])
		{
			swap(tab[i], tab[i + 1]);
			i = 0;
		}
		else
			i++;
	}
}
